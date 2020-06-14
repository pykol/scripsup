# -*- coding: utf-8 -*-

# Inscrisup - Gestion des inscriptions administratives après Parcoursup
# Copyright (c) 2019 Florian Hatat
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Utilitaires pour communiquer avec l'API REST de Parcoursup
"""

from datetime import date, datetime
import re
import requests
from dateutil.tz import gettz

from django.utils import timezone
from django.conf import settings

from .utils import parse_french_date

PARCOURSUP_ENDPOINT = "https://ws.parcoursup.fr/ApiRest/"

def parse_date_reponse(date_str):
	paris_tz = gettz('Europe/Paris')
	date_match = re.match('^(?P<jour>\d{1,2})/(?P<mois>\d{1,2})/(?P<annee>\d{4}) (?P<heure>\d{1,2}):(?P<minute>\d{1,2})$', date_str)
	return datetime(
		year=int(date_match.group('annee')),
		month=int(date_match.group('mois')),
		day=int(date_match.group('jour')),
		hour=int(date_match.group('heure')),
		minute=int(date_match.group('minute')),
		tzinfo=paris_tz,
	)

class ParcoursupError(Exception):
	"""
	Exception levée quand la discussion avec Parcoursup n'est pas
	possible.
	"""
	pass

class ParcoursupRequest:
	"""
	Légère couche d'abstraction au-dessus du module requests pour gérer
	l'envoi de requêtes à l'API Parcoursup, en incluant les données
	d'identification.
	"""
	def __init__(self, login, password, method_name=None,
			http_method='POST', data={}, endpoint=PARCOURSUP_ENDPOINT):
		self.login = login
		self.password = password
		self.response = None
		self.method_name = method_name
		self.http_method = http_method
		self.endpoint = endpoint

		self.data = data
		self.data.update({
			'identifiant': {
				'login': login,
				'pwd': password,
			}
		})

	def get_url(self):
		"""
		Construction de l'URL à laquelle il faut poster la requête.
		"""
		return '{base}{method}'.format(
			base=self.endpoint, method=self.method_name)

	def send(self):
		"""
		Envoi de la requête à Parcoursup.
		"""
		# Oui, ça a l'air idiot, mais c'est pour plus tard si jamais
		# Parcoursup nous introduit d'autres méthodes HTTP dans des
		# mises à jour de l'API.
		if self.http_method != 'POST':
			raise ValueError("Cette API ne gère pas d'autres méthodes "
					"HTTP que POST")

		self.response = requests.post(self.get_url(), json=self.data)

		self.response.raise_for_status()

		resp_json = self.response.json()
		if isinstance(resp_json, dict) and resp_json.get('retour', 'OK') == 'NOK':
			raise ParcoursupError(resp_json.get('message',
				'Erreur Parcoursup inconnue'))

		return self.response

class ParcoursupPersonne:
	GENRE_HOMME = 1
	GENRE_FEMME = 2

	def __init__(self, **kwargs):
		self.nom = kwargs.get('nom')
		self.prenom = kwargs.get('prenom')
		self.email = kwargs.get('email')
		self.adresse = kwargs.get('adresse')
		self.telephone_fixe = kwargs.get('telephone_fixe')
		self.telephone_mobile = kwargs.get('telephone_mobile')
		self.sexe = kwargs.get('sexe')
		self.code_commune = kwargs.get('code_commune')
		self.code_postal = kwargs.get('code_postal')
		self.code_pays = kwargs.get('code_pays')

	@staticmethod
	def formate_adresse(donnees):
		CODE_PAYS_FRANCE = '99100'
		code_pays = donnees.get('codepaysadresse', CODE_PAYS_FRANCE)
		libelle_ville = donnees.get('libellecommune', '')
		libelle_pays = donnees.get('libellePaysadresse', '')

		raw_adresse = '{adresse1}\n{adresse2}\n{adresse3}\n{code_postal} {ville}\n{pays}'.format(
			adresse1=donnees.get('adresse1') or '',
			adresse2=donnees.get('adresse2') or '',
			adresse3=donnees.get('adresse3') or '',
			# Orthographie affligeante. On teste les deux, pour être
			# robuste à une future correction qui casse la
			# compatibilité.
			code_postal=donnees.get('codepostal', donnees.get('codepostale')) or '',
			ville=libelle_ville,
			pays=libelle_pays)
		return re.sub(r'\n+', '\n', raw_adresse).strip()


class ParcoursupCandidat(ParcoursupPersonne):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		for field in ['code', 'date_naissance', 'commune_naissance',
			'pays_naissance', 'nationalite', 'ine', 'bac_date',
			'bac_serie', 'bac_mention',
			'etablissement_origine_uai', 'etablissement_origine_nom']:
			setattr(self, field, kwargs.get(field))

	def to_json(self):
		return {
			'codeCandidat': int(self.code),
			'ine': str(self.ine),
			'nom': str(self.nom),
			'prenom': str(self.prenom),
			'dateNaissance': self.date_naissance.strftime('%d/%m/%Y')
		}

	@classmethod
	def from_parcoursup_json(kls, donnees):
		"""
		Création d'une instance initialisée à partir des données
		Parcoursup au format JSON.
		"""
		defaults = {
			'nom': donnees['nom'],
			'prenom': donnees['prenom'],
			'email': donnees['mail'],
			'date_naissance': parse_french_date(donnees['dateNaissance']),
			'code': donnees['codeCandidat'],
			'ine': donnees['ine'],
			'adresse': kls.formate_adresse(donnees),
			'telephone_fixe': donnees['telfixe'],
			'telephone_mobile': donnees['telmobile'],
			'sexe': ParcoursupCandidat.GENRE_HOMME if donnees['sexe'] == 'M'
				else ParcoursupCandidat.GENRE_FEMME,
			'commune_naissance': donnees.get('codeCommuneNaissance'),
			'pays_naissance': donnees.get('codePaysNaissance'),
			'nationalite': donnees.get('codePaysNationalite'),
			'etablissement_origine_uai': donnees.get('codeEtablissementSco'),
			'etablissement_origine_nom': donnees.get('libelleEtablissementSco'),
			'code_commune': donnees.get('codeCommune'),
			'code_postal': donnees.get('codePostal'),
			'code_pays': donnees.get('codePaysAdresse'),
			}
		try:
			defaults['bac_date'] = date(int(donnees['anneeBac']),
				int(donnees['moisBac']), 1)
			defaults['bac_serie'] = donnees['serieBac']
			defaults['bac_mention'] = donnees['mentionBac']
		except KeyError:
			pass

		return kls(**defaults)

class ParcoursupResponsableLegal(ParcoursupPersonne):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	@classmethod
	def from_parcoursup_json(kls, donnees, rang=1):
		"""
		Création d'une instance à partir des données Parcoursup au
		format JSON. Le rang du responsable légal peut être choisi en
		paramètre. Si aucun responsable légal de ce rang n'existe, la
		méthode renvoie None.
		"""
		try:
			return kls(
				nom=donnees['nomRL{}'.format(rang)],
				prenom=donnees['prenomRL{}'.format(rang)],
				email=donnees['mailRL{}'.format(rang)],
				telephone_fixe=donnees['telRL{}'.format(rang)],
				telephone_mobile='',
				adresse='',
				#TODO adresse
			)
		except Exception as e:
			return None

class ParcoursupProposition:
	ETAT_ATTENTE = 0
	ETAT_ACCEPTEE = 1
	ETAT_ACCEPTEE_AUTRES_VOEUX = 2
	ETAT_REFUSEE = 3

	def __init__(self, **kwargs):
		self.session = kwargs.get('session')
		self.code_formation = kwargs.get('code_formation')
		self.code_etablissement = kwargs.get('code_etablissement')
		self.cesure = kwargs.get('cesure')
		self.internat = kwargs.get('internat')
		self.etat = kwargs.get('etat')
		self.date = kwargs.get('date')

	@classmethod
	def from_parcoursup_json(kls, donnees):
		"""
		Création d'une instance initialisée à partir des données
		Parcoursup au format JSON.
		"""
		return kls(
			code_formation=int(donnees['codeFormationPsup']),
			code_etablissement=donnees['codeEtablissementAffectation'],
			cesure=donnees['cesure'] == "1",
			internat=donnees['internat'] == "1",
			date=parse_date_reponse(donnees['dateReponse']),
			etat=int(donnees['codeSituation']),
			)

class ParcoursupRest:
	def __init__(self, login="XXX", password="XXX",
			code_etablissement="XXX"):
		self.login = login
		self.password = password
		self.code_etablissement = code_etablissement

	def get_candidats_admis(self, **kwargs):
		"""
		Accès générique à la méthode getCandidatsAdmis de l'API
		Parcoursup.

		Cette méthode est déclinée en autres méthodes plus simples à
		utiliser, en fonction des paramètres que l'on veut renseigner.
		"""
		parcoursup_args = {
			'code_candidat': ('codeCandidat', int),
			'formation': ('codeFormationpsup', int),
		}
		request_data = {
			'codeEtablissement': str(self.code_etablissement)
		}
		args_inconnus = []
		for kwarg, valeur in kwargs.items():
			try:
				psup_arg, coercion = parcoursup_args[kwarg]
				request_data[psup_arg] = coercion(valeur)
			except KeyError as e:
				args_inconnus.append(e.args[0])
		if args_inconnus:
			raise TypeError("Unexpected named parameters {}".format(
				', '.join(args_inconnus)))

		request = ParcoursupRequest(self.login, self.password,
				method_name='getCandidatsAdmis',
				data=request_data)
		response = request.send()

		# Mise en forme de la réponse
		candidats = []
		if response.status_code != 200:
			raise ParcoursupError

		for psup_json in response.json():
			candidats.append(self.parse_parcoursup_admission(psup_json))
		return candidats

	def get_candidat(self, code_candidat):
		"""
		Recherche des informations sur un candidat admis d'après son
		numéro de dossier.
		"""
		return self.get_candidats_admis(code_candidat=code_candidat)[0]

	@staticmethod
	def parse_parcoursup_admission(psup_json):
		"""
		Prend en paramètre le JSON envoyé par l'interface synchrone de
		Parcoursup et renvoie les informations structurées avec les
		classes ParcoursupCandidat, ParcoursupResponsableLegal et
		ParcoursupProposition.
		"""
		donnees = requests.utils.CaseInsensitiveDict(data=psup_json)
		candidat = ParcoursupCandidat.from_parcoursup_json(donnees)
		proposition = ParcoursupProposition.from_parcoursup_json(donnees)
		responsables = []
		for rang in (1, 2):
			responsable = ParcoursupResponsableLegal.from_parcoursup_json(donnees,
						rang=rang)
			if responsable is not None:
				responsables.append(responsable)

		return {
			'candidat': candidat,
			'proposition': proposition,
			'responsables': responsables,
		}


	# Codes des statuts d'inscription de l'API Parcoursup
	INSCRIPTION_PRINCIPALE = 1
	INSCRIPTION_DOUBLE_CURSUS = 2
	INSCRIPTION_ANNULEE = 3
	INSCRIPTION_PARALLELE = 4
	INSCRIPTION_PARALLELE_SECONDAIRE = 5

	def maj_inscription(self, candidat, formation,
			etat_inscription):
		"""
		Mise à jour de l'état d'inscription d'un candidat.
		"""
		request_data = candidat.to_json()
		request_data.update({
			'codeFormationPsup': int(formation),
			'codeFormation1': str(formation),
			'codeSISE': int(formation),
			'etatInscription': int(etat_inscription),
			'codeEtablissementAffectation': str(self.code_etablissement),
		})
		request = ParcoursupRequest(self.login, self.password,
				method_name='majInscriptionAdministrative',
				data=request_data)
		return request.send()

	def requete_test(self):
		"""
		Envoie la requête test prévue par Parcoursup. Cette requête doit
		être envoyée avant d'avoir accès à l'API d'admission.
		"""
		candidat = ParcoursupCandidat(
			code=1, nom="Bernard", prenom="Minet",
			date_naissance=date(1789, 7, 14),
			ine="0123456789AB")

		return self.maj_inscription(candidat=candidat,
			formation=42, code_sise=1,
			statut_inscription=INSCRIPTION_PRINCIPALE)

# -*- coding: utf8 -*-

# scripsup - Inscription en ligne en CPGE
# Copyright (c) 2020 Florian Hatat
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
Vues gérant les appels de l'API REST de Parcoursup
"""

import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.utils import timezone

import requests

from inscrire.models import ParcoursupUser, ParcoursupMessageRecuLog, \
		Candidat, ResponsableLegal, Formation, EtatVoeu, Voeu, \
		HistoriqueVoeu
import inscrire.lib.utils as utils
from inscrire.lib.parcoursup_rest import ParcoursupRest

class ParcoursupClientView(View):
	"""
	Vue générique pour traiter une requête entrante en provenance de
	Parcoursup.

	Elle vérifie que la requête est bien au format JSON et qu'elle
	contient des données d'identification valides. Elle enregistre la
	requête dans le journal des messages Parcoursup.

	Le traitement de la requête elle-même est délégué à la méthode
	self.parcoursup(), qui peut se servir notamment de l'attribut
	self.json, qui contient les données JSON décodées.
	"""
	http_method_names = ['post']
	endpoint = "undef"

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.json = None
		self.user = None

	def identification(self):
		"""
		Vérifie que la requête possède bien les données
		d'identification.
		"""
		try:
			self.user = ParcoursupUser.objects.authenticate(
				username=self.json['identifiant']['login'],
				password=self.json['identifiant']['pwd'])
			return True
		except:
			return False

	def entree_json(self):
		"""
		Vérifie que la requête contient bien des données en JSON.
		"""
		if 'application/json' != self.request.content_type:
			return False

		try:
			psup_json = json.loads(self.request.body.decode('utf-8'))
			self.json = requests.utils.CaseInsensitiveDict(data=psup_json)
			return True
		except (json.JSONDecodeError, UnicodeDecodeError):
			return False

	def json_response(self, ok, msg_log=None, message=None, status_code=None):
		"""
		Construction d'une réponse pour Parcoursup
		"""
		data = {
			'message': message
		}

		if ok:
			data['retour'] = 'OK'

			if data['message'] is None:
				data['message'] = "Requete correctement traitee"

			status_code = status_code if status_code is not None else 200
		else:
			data['retour'] = 'NOK'

			if data['message'] is None:
				data['message'] = "Erreur lors du traitement"

			status_code = status_code if status_code is not None else 500

		response = JsonResponse(data)
		response.status_code = status_code

		if msg_log is not None:
			msg_log.succes = data['retour'] == 'OK'
			msg_log.message = data['message']

		return response

	# On redéfinit cette méthode uniquement afin de la décorer, car les
	# appels de l'API REST ne doivent pas être protégés par le jeton
	# CSRF de Django.
	@method_decorator(csrf_exempt)
	def dispatch(self, *args, **kwargs):
		return super().dispatch(*args, **kwargs)

	def get_ip_source(self):
		"""
		Détermine l'IP à l'origine de la requête
		"""
		try:
			return self.request.META['HTTP_X_FORWARDED_FOR'].split(',')[0]
		except:
			return self.request.META['REMOTE_ADDR']

	def post(self, request):
		"""
		Traitement des données issues d'une requête POST provenant de
		Parcoursup.

		Cette méthode vérifie que les données sont au format JSON et que
		la requête possède des informations d'identification valides,
		puis confie le reste du traitement à la méthode
		self.parcoursup(). Cette dernière doit renvoyer elle-même la
		réponse au format JSON, en s'aidant éventuellement de la méthode
		self.json_response(). Si elle lève une exception, une réponse
		d'erreur générique est renvoyée à Parcoursup.
		"""
		msg_log = ParcoursupMessageRecuLog(date=timezone.now(),
				ip_source=self.get_ip_source(),
				endpoint=self.endpoint,
				payload=self.request.body)

		if not self.entree_json():
			msg_log.succes = False
			msg_log.message = "Les données soumises ne sont pas au format JSON valide"
			msg_log.save()
			return self.json_response(False, message=msg_log.message)

		if not self.identification():
			msg_log.succes = False
			msg_log.message = "Données d'identification incorrectes"
			msg_log.save()
			return self.json_response(False, message=msg_log.message)

		msg_log.user = self.user

		try:
			response = self.parcoursup(msg_log=msg_log)
		except:
			response = self.json_response(False, msg_log=msg_log)

		msg_log.save()
		return response

class AdmissionView(ParcoursupClientView):
	"""
	Vue appelée par Parcoursup pour transmettre la réponse d'un candidat
	à une proposition d'admission.
	"""
	endpoint = "admissionCandidat"

	def parcoursup(self, msg_log=None):
		donnees = self.json.get('donneesCandidat', self.json) # Bug 2019 Parcoursup

		try:
			adresse = ParcoursupRest.formate_adresse(donnees)
		except:
			adresse = '(Inconnue)'

		try:
			candidat = Candidat.objects.get(dossier_parcoursup=donnees['codeCandidat'])
			envoyer_email_bienvenue = False
		except Candidat.DoesNotExist:
			# Création du candidat
			candidat = Candidats.objects.bienvenue(
					first_name=donnees['prenom'],
					last_name=donnees['nom'],
					email=donnees['mail'],
					dossier_parcoursup=donnees['codeCandidat'])
			envoyer_email_bienvenue = True

		candidat.date_naissance = utils.parse_french_date(donnees['dateNaissance'])
		candidat.ine = donnees['ine']
		candidat.last_name = donnees['nom']
		candidat.first_name = donnees['prenom']
		candidat.telephone = donnees.get('telfixe', '')
		candidat.telephone_mobile = donnees.get('telmobile', '')
		candidat.genre = Candidat.GENRE_HOMME if donnees['sexe'] == 'M' \
						else Candidat.GENRE_FEMME
		candidat.adresse = adresse
		candidat.save()

		# On détermine la proposition à laquelle fait référence le
		# message actuel.
		formation = Formation.objects.get(code_parcoursup=donnees['codeFormationPsup'])
		date_reponse = utils.parse_datetime(donnees['dateReponse'])

		# Déterminer l'état du vœu remonté par Parcoursup
		etat_voeu = EtatVoeu.ETAT_ATTENTE
		# Le candidat n'a pas encore répondu
		if donnees['codeSituation'] == '0':
			pass
		# Proposition acceptée définitivement
		elif donnees['codeSituation'] == '1':
			etat_voeu = EtatVoeu.ETAT_ACCEPTE_DEFINITIF
		# Proposition acceptée avec autres vœux en attente
		if donnees['codeSituation'] == '2':
			etat_voeu = EtatVoeu.ETAT_ACCEPTE_AUTRES
		# Proposition refusée
		if donnees['codeSituation'] == '3':
			etat_voeu = EtatVoeu.ETAT_REFUSE

		try:
			voeu = Voeu.objects.get(candidat=candidat,
					formation=formation,
					internat=donnees.get('internat', '0') == '1')
		except Voeu.DoesNotExist:
			voeu = Voeu(candidat=candidat,
					formation=formation,
					etat=etat_voeu)

		voeu.save()

		# Envoi de l'e-mail de bienvenue
		candidat.email_bienvenue()

		return self.json_response(True, msg_log=msg_log)

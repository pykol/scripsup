# -*- coding:utf8 -*-

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

from django.db import models
from django.conf import settings

from inscrire.lib.parcoursup_rest import ParcoursupCandidat, \
		ParcoursupRest, ParcoursupPersonne, ParcoursupProposition
from .personnes import Candidat, Pays, Commune, ResponsableLegal
from .formation import Etablissement, Formation
from .fiches import Fiche

class ParcoursupUserManager(models.Manager):
	def authenticate(self, username, password):
		"""
		Renvoie l'utilisateur désigné par le nom d'utilisateur et le mot
		de passe donnés en paramètre.

		Lève l'exception ParcoursupUser.DoesNotExist si l'utilisateur
		n'existe pas ou si le mot de passe n'est pas correct.
		"""
		parcoursup_user = self.get(username=username)
		if not parcoursup_user.user.check_password(password):
			raise parcoursup_user.DoesNotExist

		return parcoursup_user

class ParcoursupUser(models.Model):
	"""
	Identifiants utilisés pour recevoir et envoyer des messages via
	l'API Parcoursup
	"""
	etablissement = models.OneToOneField(Etablissement,
			on_delete=models.CASCADE, primary_key=True)

	# Identifiants qui permettent à Parcoursup de se connecter à notre
	# service pour envoyer les admis.
	username = models.CharField(max_length=50)
	user = models.OneToOneField(settings.AUTH_USER_MODEL,
			on_delete=models.CASCADE)

	# Identifiants que l'on doit utiliser pour envoyer des données à
	# Parcoursup. Le mot de passe est stocké en clair, c'est ainsi qu'on
	# doit l'envoyer à Parcoursup dans les requêtes.
	adresse_api = models.URLField(max_length=300)
	remontee_username = models.CharField(max_length=50)
	remontee_password = models.CharField(max_length=128)

	objects = ParcoursupUserManager()

	class Meta:
		verbose_name = "utilisateur Parcoursup"
		verbose_name_plural = "utilisateurs Parcoursup"

	_parcoursup_rest = None

	@property
	def parcoursup_rest(self):
		if self._parcoursup_rest is None:
			self._parcoursup_rest = ParcoursupRest(
					login=self.remontee_username,
					password=self.remontee_password,
					code_etablissement=self.etablissement.numero_uai)
		return self._parcoursup_rest

	def import_candidat(self, psup):
		"""
		Import des données Parcoursup dans la base de données du serveur
		d'inscription.

		Renvoie l'instance du modèle Candidat correspondant au candidat.

		Prend en paramètre un dictionnaire renvoyé par
		ParcoursupRest.parse_parcoursup_admission.
		"""
		# Création ou mise à jour du candidat
		try:
			candidat = Candidat.objects.get(dossier_parcoursup=psup['candidat'].code)
		except Candidat.DoesNotExist:
			candidat = Candidat.objects.bienvenue(
					first_name=psup['candidat'].prenom,
					last_name=psup['candidat'].nom,
					email=psup['candidat'].email,
					dossier_parcoursup=psup['candidat'].code,
				)
		candidat.genre = Candidat.GENRE_HOMME \
				if psup['candidat'].sexe == ParcoursupPersonne.GENRE_HOMME \
				else Candidat.GENRE_FEMME
		candidat.telephone = psup['candidat'].telephone_fixe or ''
		candidat.telephone_mobile = psup['candidat'].telephone_mobile or ''
		candidat.adresse = psup['candidat'].adresse
		candidat.date_naissance = psup['candidat'].date_naissance
		candidat.commune_naissance = Commune.objects.filter(code_insee=psup['candidat'].commune_naissance).first()
		candidat.pays_naissance = Pays.objects.filter(code_iso2=psup['candidat'].pays_naissance).first()
		candidat.nationalite = Pays.objects.filter(code_iso2=psup['candidat'].nationalite).first()
		candidat.ine = psup['candidat'].ine
		candidat.bac_date = psup['candidat'].bac_date
		candidat.bac_serie = psup['candidat'].bac_serie
		candidat.bac_mention = {
				'P': Candidat.BAC_MENTION_PASSABLE,
				'AB': Candidat.BAC_MENTION_ASSEZBIEN,
				'B': Candidat.BAC_MENTION_BIEN,
				'TB': Candidat.BAC_MENTION_TRESBIEN,
			}.get(psup['candidat'].bac_mention)
		candidat.save()

		# Détermination du vœu concerné
		etat_voeu = {
				ParcoursupProposition.ETAT_ATTENTE: Voeu.ETAT_ATTENTE,
				ParcoursupProposition.ETAT_ACCEPTEE_AUTRES_VOEUX: Voeu.ETAT_ACCEPTE_AUTRES,
				ParcoursupProposition.ETAT_ACCEPTEE: Voeu.ETAT_ACCEPTE_DEFINITIF,
				ParcoursupProposition.ETAT_REFUSEE: Voeu.ETAT_REFUSE,
				}.get(psup['proposition'].etat)

		formation = Formation.objects.get(
				code_parcoursup=psup['proposition'].code_formation,
				etablissement=self.etablissement)
		voeu, voeu_created = Voeu.objects.get_or_create(
				candidat=candidat,
				formation=formation,
				internat=psup['proposition'].internat,
				cesure=psup['proposition'].cesure,
				defaults={'etat': etat_voeu})
		if voeu.etat != etat_voeu:
			HistoriqueVoeu(voeu=voeu, etat=etat_voeu,
					date=timezone.now()).save()
			voeu.etat = etat_voeu
			voeu.save()

		# Import des responsables légaux
		# Aucune clé primaire n'est transmise par Parcoursup. Pour
		# éviter des doublons, on ne crée les responsables que lors du
		# premier ajout du candidat. Pour la suite, c'est au candidat
		# de mettre à jour manuellement les données dans son dossier
		# d'inscription.
		if not candidat.responsables.all():
			for psup_resp in psup['responsables']:
				if psup_resp.sexe == ParcoursupPersonne.GENRE_HOMME:
					genre = Candidat.GENRE_HOMME
				elif psup_resp.sexe == ParcoursupPersonne.GENRE_FEMME:
					genre = Candidat.GENRE_FEMME
				else:
					genre = None
				ResponsableLegal(
						candidat=candidat,
						genre=genre,
						last_name=psup_resp.nom,
						first_name=psup_resp.prenom,
						telephone=psup_resp.telephone_fixe or '',
						telephone_mobile=psup_resp.telephone_mobile or '',
						adresse=psup_resp.adresse).save()

		# Mise à jour des fiches d'inscription
		Fiche.objects.create_or_update_applicable(voeu,
				parcoursup=psup)

		return candidat

	def get_candidats_admis(self):
		"""
		Met à jour la liste de tous les candidats admis dans
		l'établissement.
		"""
		res = []
		for candidat in self.parcoursup_rest.get_candidats_admis():
			try:
				res.append(self.import_candidat(candidat))
			except Exception as e:
				# TODO reporting à l'admin
				pass
		return res

	def get_candidat_admis(self, code_candidat):
		"""
		Met à jour un candidat
		Renvoie les informations concernant un candidat admis.
		"""
		return self.import_candidat(
				self.parcoursup_rest.get_candidat(code_candidat))

	def set_inscription(self, candidat):
		"""
		Envoie à Parcoursup l'état d'inscription
		"""
		psup_candidat = ParcoursupCandidat(
				code=candidat.dossier_parcoursup,
				ine=candidat.ine,
				nom=candidat.last_name,
				prenom=candidat.first_name,
				date_naissance=candidat.date_naissance)
		self.parcoursup_rest.maj_inscription(
				psup_candidat,
				candidat.voeu_actuel.formation.code_parcoursup,
				ParcoursupRest.INSCRIPTION_PRINCIPALE)

	def envoi_candidat_test(self):
		"""
		Active les push de Parcoursup en envoyant un candidat de test.
		"""
		self.parcoursup_rest.requete_test()

class ParcoursupMessageRecuLog(models.Model):
	"""
	Journal des messages reçus depuis Parcoursup
	"""
	date = models.DateTimeField()
	ip_source = models.GenericIPAddressField()
	user = models.ForeignKey(ParcoursupUser, on_delete=models.SET_NULL,
			blank=True, null=True)
	endpoint = models.CharField(max_length=100)
	message = models.CharField(max_length=200)
	succes = models.BooleanField()
	payload = models.BinaryField(verbose_name="données reçues",
			blank=True, default=b'', null=True)

	class Meta:
		verbose_name = "message reçu Parcoursup"
		verbose_name_plural = "messages reçus Parcoursup"

class ParcoursupMessageEnvoyeLog(models.Model):
	"""
	Journal des messages envoyés à Parcoursup
	"""
	date = models.DateTimeField()

	class Meta:
		verbose_name = "message envoyé Parcoursup"
		verbose_name_plural = "messages envoyés Parcoursup"

class EtatVoeu(models.Model):
	"""
	Base pour un modèle qui stocke l'état (la réponse du candidat) à un
	vœu.
	"""
	class Meta:
		abstract = True

	ETAT_ATTENTE = 0
	ETAT_ACCEPTE_AUTRES = 1
	ETAT_ACCEPTE_DEFINITIF = 2
	ETAT_REFUSE = 3
	ETAT_CHOICES = (
		(ETAT_ATTENTE, "en liste d'attente"),
		(ETAT_ACCEPTE_AUTRES, "accepté avec autres vœux en attente"),
		(ETAT_ACCEPTE_DEFINITIF, "accepté définitivement"),
		(ETAT_REFUSE, "refusé par le candidat"),
	)
	etat = models.PositiveSmallIntegerField(choices=ETAT_CHOICES)

class Voeu(EtatVoeu):
	"""
	Vœu d'un candidat dans Parcoursup
	"""
	candidat = models.ForeignKey(Candidat, on_delete=models.CASCADE)
	formation = models.ForeignKey(Formation, on_delete=models.CASCADE)
	internat = models.BooleanField()
	cesure = models.BooleanField()

	class Meta:
		verbose_name = "vœu"
		verbose_name_plural = "vœux"

class HistoriqueVoeu(EtatVoeu):
	"""
	Historique des réponses d'un candidat à un vœu donné
	"""
	voeu = models.ForeignKey(Voeu, on_delete=models.CASCADE)
	date = models.DateTimeField()

	class Meta:
		verbose_name = "historique de vœu"
		verbose_name_plural = "historiques de vœu"

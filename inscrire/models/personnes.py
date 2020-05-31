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
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone

User = get_user_model()

class Commune(models.Model):
	"""
	Commune française
	"""
	code_insee = models.CharField(max_length=5, primary_key=True)
	nom_clair = models.CharField(max_length=200)
	nom_riche = models.CharField(max_length=200)
	libelle = models.CharField(max_length=200)

	class Meta:
		verbose_name = "commune"
		verbose_name_plural = "communes"

	def __str__(self):
		return self.libelle

class Pays(models.Model):
	"""
	Pays
	"""
	code_iso2 = models.CharField(max_length=2, primary_key=True)
	code_iso3 = models.CharField(max_length=3, unique=True)
	num_iso = models.PositiveSmallIntegerField(unique=True)
	libelle = models.CharField(max_length=200)

	class Meta:
		verbose_name = "pays"
		verbose_name_plural = "pays"

	def __str__(self):
		return self.libelle

class Profession(models.Model):
	"""
	Catégorie socio-professionnelle
	"""
	code = models.PositiveSmallIntegerField(primary_key=True)
	libelle_court = models.CharField(max_length=200)
	libelle_long = models.CharField(max_length=200)

	class Meta:
		verbose_name = "profession"
		verbose_name_plural = "professions"

	def __str__(self):
		return self.libelle_court

class Personne(models.Model):
	"""
	Classe abstraite qui regroupe les champs communs décrivant une
	personne (candidat ou responsable légal) dans Parcoursup.
	"""
	class Meta:
		abstract = True

	GENRE_HOMME = 1
	GENRE_FEMME = 2
	GENRE_CHOICES = (
			(GENRE_HOMME, "homme"),
			(GENRE_FEMME, "femme"),
		)
	genre = models.PositiveSmallIntegerField(choices=GENRE_CHOICES)
	last_name = models.CharField(verbose_name="nom", max_length=100)
	first_name = models.CharField(verbose_name="prénom", max_length=100)
	telephone = models.CharField(verbose_name="téléphone",
			max_length=20, blank=True, null=False, default='')
	telephone_mobile = models.CharField(verbose_name="téléphone mobile",
			max_length=20, blank=True, null=False, default='')
	adresse = models.TextField(blank=True, null=False, default='(Inconnue)')

	def __str__(self):
		return "{} {}".format(self.first_name, self.last_name)

class CandidatManager(models.Manager):
	def bienvenue(self, first_name, last_name, email,
			dossier_parcoursup, **kwargs):
		"""
		Crée un candidat la première fois que Parcoursup nous signale
		son admission dans une formation.
		"""
		candidat_user = User.objects.create_user(
				email=email,
				first_name=first_name,
				last_name=last_name,
				role=User.ROLE_ETUDIANT)
		candidat_user.save()

		candidat = Candidat(
				first_name=first_name,
				last_name=last_name,
				dossier_parcoursup=dossier_parcoursup,
				user=candidat_user, **kwargs)

		return candidat

class Candidat(Personne):
	"""
	Candidat

	Les données sont normalement obtenues via l'API Parcoursup
	"""
	dossier_parcoursup = models.IntegerField(verbose_name="numéro Parcoursup",
			primary_key=True)
	date_naissance = models.DateField(verbose_name="date de naissance",
			blank=True, null=True)
	commune_naissance = models.ForeignKey(Commune,
			on_delete=models.SET_NULL, blank=True, null=True)
	pays_naissance = models.ForeignKey(Pays, on_delete=models.SET_NULL,
			blank=True, null=True, related_name='candidats_naissance')
	nationalite = models.ForeignKey(Pays, on_delete=models.SET_NULL,
			blank=True, null=True, related_name='candidats_nationalite')

	ine = models.CharField(blank=True, null=True,
			max_length=11, verbose_name="INE (numéro d'étudiant)",
			unique=True)
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

	# Informations concernant le baccalauréat
	bac_date = models.DateField(blank=True,
			null=True) # Le jour n'est pas significatif, on ne regarde que le mois et l'année
	bac_serie = models.CharField(max_length=8, blank=True, null=True)
	BAC_MENTION_PASSABLE = 0
	BAC_MENTION_ASSEZBIEN = 1
	BAC_MENTION_BIEN = 2
	BAC_MENTION_TRESBIEN = 3
	BAC_MENTION_CHOICES = (
			(BAC_MENTION_PASSABLE, "passable"),
			(BAC_MENTION_ASSEZBIEN, "assez bien"),
			(BAC_MENTION_BIEN, "bien"),
			(BAC_MENTION_TRESBIEN, "très bien"),
		)
	bac_mention = models.PositiveSmallIntegerField(choices=BAC_MENTION_CHOICES,
			blank=True, null=True)

	email_bienvenue_envoye = models.BooleanField(
			verbose_name="message de bienvenue envoyé",
			default=False)

	objects = CandidatManager()

	class Meta:
		verbose_name = "candidat"
		verbose_name_plural = "candidats"

	@property
	def voeu_actuel(self):
		"""
		Renvoie le vœu actuellement accepté par le candidat
		"""
		from .parcoursup import Voeu # Import ici, sinon dépendance circulaire
		return self.voeu_set.get(etat__in=(Voeu.ETAT_ACCEPTE_AUTRES,
			Voeu.ETAT_ACCEPTE_DEFINITIF))

	def email_bienvenue(self, request, force=False):
		"""
		Envoyer au candidat l'e-mail de bienvenue qui lui permet
		d'activer son compte.
		"""
		if not force and self.email_bienvenue_envoye:
			return

		voeu_actuel = self.voeu_actuel
		render_context = {
				'candidat': self,
				'formation': voeu_actuel.formation,
				'voeu': voeu_actuel,
				'lien_activation': request.build_absolute_uri(reverse('password_reset_confirm',
					args=(
						urlsafe_base64_encode(force_bytes(self.user.pk)),
						default_token_generator.make_token(self.user)
					)))
				}

		send_mail(
				render_to_string('inscrire/email_bienvenue_candidat_subject.txt',
					context=render_context).strip(),
				render_to_string('inscrire/email_bienvenue_candidat_message.txt',
					context=render_context).strip(),
				"{email}".format(
					etablissement=voeu_actuel.formation.etablissement,
					email=voeu_actuel.formation.etablissement.email),
				("{candidat_prenom} {candidat_nom} <{email}>".format(
					candidat_prenom=str(self.user.first_name),
					candidat_nom=str(self.user.last_name),
					email=str(self.user.email)),),
				html_message=render_to_string('inscrire/email_bienvenue_candidat_message.html',
					context=render_context).strip()
			)

		self.email_bienvenue_envoye = True
		self.save()

		self.log("E-mail d'activation du compte envoyé au candidat")

	def log(self, message, date=None):
		if date is None:
			date = timezone.now()
		CandidatActionLog(candidat=self, message=message,
				date=date).save()

class ResponsableLegal(Personne):
	"""
	Coordonnées du responsable légal d'un candidat
	"""
	candidat = models.ForeignKey(Candidat, related_name='responsables',
			on_delete=models.CASCADE)
	profession = models.ForeignKey(Profession,
			on_delete=models.SET_DEFAULT,
			default=99)

	class Meta:
		verbose_name = "responsable légal"
		verbose_name_plural = "responsables légaux"

class CandidatActionLog(models.Model):
	"""
	Journal des actions effectuées sur le compte d'un candidat
	"""
	candidat = models.ForeignKey(Candidat, on_delete=models.CASCADE)
	message = models.TextField(blank=True, null=False, default="")
	date = models.DateTimeField()

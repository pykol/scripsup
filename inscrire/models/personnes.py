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

User = get_user_model()

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
				username=email,
				first_name=donnees['prenom'],
				last_name=donnees['nom'],
				role=User.ROLE_CANDIDAT)
		candidat_user.save()

		candidat = Candidat(
				dossier_parcoursup=donnees['codeCandidat'],
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
	ine = models.CharField(blank=True, null=True,
			max_length=11, verbose_name="INE (numéro d'étudiant)",
			unique=True)
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

	objects = CandidatManager()

	@property
	def voeu_actuel(self):
		"""
		Renvoie le vœu actuellement accepté par le candidat
		"""
		from .parcoursup import Voeu # Import ici, sinon dépendance circulaire
		return self.voeu_set.get(etat__in=(Voeu.ETAT_ACCEPTE_AUTRES,
			Voeu.ETAT_ACCEPTE_DEFINITIF))

	def email_bienvenue(self):
		"""
		Envoyer au candidat l'e-mail de bienvenue qui lui permet
		d'activer son compte.
		"""
		voeu_actuel = self.voeu_actuel
		render_context = {
				'candidat': self,
				'formation': voeu_actuel.formation,
				'voeu': voeu_actuel,
				'lien_activation': reverse('password_reset_confirm',
					args=(
						urlsafe_base64_encode(force_bytes(self.pk)),
						default_token_generator.make_token(self)
					))
				}

		send_mail(
				render_to_string('inscrire/email_bienvenue_candidat_subject.txt',
					context=render_context).strip(),
				render_to_string('inscrire/email_bienvenue_candidat_message.txt',
					context=render_context).strip(),
				"{etablissement} <{email}>".format(
					etablissement=voeu_actuel.formation.etablissement,
					email=voeu_actuel.formation.etablissement.email)
				("{candidat} <{email}>".format(
					candidat=str(self),
					email=self.user.email),),
				html_message=render_to_string('inscrire/email_bienvenue_candidat_message.html',
					context=render_context).strip()
			)

class ResponsableLegal(Personne):
	"""
	Coordonnées du responsable légal d'un candidat
	"""
	candidat = models.ForeignKey(Candidat, related_name='responsables',
			on_delete=models.CASCADE)

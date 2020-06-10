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

from .fields import Lettre23Field
from .personnes import Candidat

class Etablissement(models.Model):
	"""
	Établissement scolaire
	"""
	numero_uai = Lettre23Field(length=8, unique=True,
			verbose_name="UAI", primary_key=True)
	nom = models.CharField(max_length=200)
	email = models.EmailField(verbose_name="adresse e-mail",
			help_text="Adresse de contact proposée aux candidats",
			blank=True, null=False, default="")
	inscriptions = models.BooleanField(default=False,
			help_text="Indique s'il s'agit d'un établissement dont le "
			"site actuel gère les inscriptions")
	commune = models.ForeignKey('Commune', on_delete=models.SET_NULL,
			blank=True, null=True)

	class Meta:
		verbose_name = "établissement"
		verbose_name_plural = "établissements"
		ordering = ["numero_uai"]

	def __str__(self):
		return "{} {}".format(self.numero_uai, self.nom)

class Formation(models.Model):
	"""
	Description d'une formation dispensée dans l'établissement
	"""
	nom = models.CharField(max_length=100)
	code_parcoursup = models.SmallIntegerField(unique=True, null=True,
			blank=True)
	# groupe_parcoursup = models.SmallIntegerField()
	etablissement = models.ForeignKey(Etablissement,
			on_delete=models.CASCADE)
	slug = models.SlugField(unique=True)

	# Code du module élémentaire de formation correspondant dans la
	# nomenclature éducation nationale.
	code_mef = models.CharField(max_length=11)

	class Meta:
		verbose_name = "formation"
		verbose_name_plural = "formations"
		constraints = [
			models.UniqueConstraint(
				fields=('code_mef', 'etablissement'),
				name='code_mef_unique'),
			models.UniqueConstraint(
				fields=('code_parcoursup', 'etablissement'),
				name='code_parcoursup_unique'),
		]

	def __str__(self):
		return self.nom

	def candidats(self):
		from .parcoursup import Voeu
		return Candidat.objects.filter(
				voeu__formation=self,
				voeu__etat__in=(Voeu.ETAT_ACCEPTE_AUTRES,
					Voeu.ETAT_ACCEPTE_DEFINITIF))

	def candidats_incomplets(self):
		"""
		Liste des candidats dont le dossier n'est pas encore complet
		"""
		from .fiches import Fiche
		return self.candidats().filter(fiche__etat=Fiche.ETAT_EDITION).distinct()
	
	def candidats_complets(self):
		"""
		Liste des candidats dont le dossier est complet
		"""
		from .fiches import Fiche
		return self.candidats().exclude(fiche__etat=Fiche.ETAT_EDITION).distinct()

class MefMatiere(models.Model):
	"""
	Matière
	"""
	code = models.CharField(max_length=6, primary_key=True)
	libelle_court = models.CharField(max_length=100)
	libelle_long = models.CharField(max_length=100)
	libelle_edition = models.CharField(max_length=100)

	class Meta:
		verbose_name = "matière MEF"
		verbose_name_plural = "matières MEF"

	def __str__(self):
		return self.libelle_edition

class MefOption(models.Model):
	"""
	Option ouverte dans un module élémentaire de formation
	"""
	MODALITE_OBLIGATOIRE = 1
	MODALITE_FACULTATIVE = 2
	MODALITE_CHOICES = (
			(MODALITE_OBLIGATOIRE, "obligatoire"),
			(MODALITE_FACULTATIVE, "facultative"),
		)
	modalite = models.PositiveSmallIntegerField(verbose_name="modalité",
			choices=MODALITE_CHOICES)
	rang = models.PositiveSmallIntegerField()
	matiere = models.ForeignKey(MefMatiere, on_delete=models.CASCADE)
	formation = models.ForeignKey(Formation, on_delete=models.CASCADE)
	inscriptions = models.BooleanField(default=False,
			help_text="Indique si l'option est présentée aux candidats "
			"afin qu'ils la choisissent lors de l'inscription.")

	class Meta:
		verbose_name = "option MEF"
		verbose_name_plural = "options MEF"

	def __str__(self):
		if self.modalite == self.MODALITE_OBLIGATOIRE:
			return "{} ({}, rang {})".format(self.matiere,
					self.get_modalite_display(), self.rang)
		else:
			return "{} ({})".format(self.matiere,
					self.get_modalite_display())

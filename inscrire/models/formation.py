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

from operator import or_
from functools import reduce

from django.db import models
from django.contrib.contenttypes.models import ContentType

from .fields import Lettre23Field
from .personnes import Candidat

class ChampExclu(models.Model):
	"""Champ à exclure"""
	fiche = models.ForeignKey(ContentType, on_delete = models.CASCADE)
	champ = models.CharField(max_length = 255)

	@classmethod
	def mise_a_jour(cls):
		"""Peuple la table"""
		from .fiches import all_fiche
		ancienne_liste = cls.objects.all()
		nouvelle_liste = []
		for fiche in all_fiche:
			if fiche._meta.model_name != 'fichepiecejustificative':
				for field in fiche._meta.get_fields():
					if not field.name in ('id', 'polymorphic_ctype', 'valide', 'fiche_ptr', 'etat', 'candidat'):
						item, created = cls.objects.get_or_create(
							fiche = ContentType.objects.get_for_model(fiche),
							champ = field.name)
						nouvelle_liste.append(item.id)
		ancienne_liste.exclude(id__in = nouvelle_liste).delete()

	def __str__(self):
		return "{}__{}".format(self.fiche, self.champ)

class Etablissement(models.Model):
	"""
	Établissement scolaire
	"""
	numero_uai = Lettre23Field(length=8, unique=True,
			verbose_name="UAI", primary_key=True)
	nom = models.CharField(max_length=200)
	email = models.EmailField(verbose_name="adresse e-mail par défaut",
			help_text="Adresse de contact proposée aux candidats si aucune adresse n'est renseignée pour une formation",
			blank=True, null=False, default="")
	email_pieces_justificatives = models.EmailField(verbose_name="adresse e-mail pièces justificatives",
			help_text="Adresse à laquelle le candidat doit envoyer les pièces justificatives",
			blank=True, null=False, default="")
	inscriptions = models.BooleanField(default=False,
			help_text="Indique s'il s'agit d'un établissement dont le "
			"site actuel gère les inscriptions")
	commune = models.ForeignKey('Commune', on_delete=models.SET_NULL,
			blank=True, null=True)

	def fiches_limit():
		from .fiches import all_fiche
		return reduce(or_,
			[models.Q(app_label=fiche._meta.app_label, model=fiche._meta.model_name)
				for fiche in all_fiche])

	fiches = models.ManyToManyField(ContentType, limit_choices_to = fiches_limit, help_text = "Sélectionnez les fiches à inclure.</br>")

	champs_exclus = models.ManyToManyField(ChampExclu, help_text = "Sélectionnez les champs dont vous ne voulez pas.</br>")

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
	email = models.EmailField(verbose_name="adresse e-mail",
			help_text="Adresse de contact proposée aux candidats pour cette formation",
			blank=True, null=False, default="")
	email_pieces_justificatives = models.EmailField(verbose_name="adresse e-mail pièces justificatives",
			help_text="Adresse spécifique à cette formation à laquelle le candidat doit envoyer les pièces justificatives",
			blank=True, null=False, default="")
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


class PieceJustificative(models.Model):
	"""Pièce que le candidat peut ou doit envoyer"""
	MODALITE_OBLIGATOIRE = 1
	MODALITE_FACULTATIVE = 2
	MODALITE_CHOICES = (
			(MODALITE_OBLIGATOIRE, "obligatoire"),
			(MODALITE_FACULTATIVE, "facultative"),
		)
	modalite = models.PositiveSmallIntegerField(default = MODALITE_OBLIGATOIRE, verbose_name="modalité",
			choices=MODALITE_CHOICES)
	etablissement = models.ForeignKey(Etablissement, null = True, blank = True,
			default = None,	on_delete=models.CASCADE,
			help_text = "Ne pas renseigner si la pièce est spécifique à une formation")
	formation = models.ForeignKey(Formation, null = True, blank = True,
			default = None, on_delete=models.CASCADE,
			help_text = "Renseigner si la pièce est spécifique à cette formation")
	nom = models.CharField(max_length = 100)
	descriptif = models.TextField(default = "") # descriptif de la pièce
	email_specifique = models.EmailField(default = "", verbose_name="adresse e-mail pour cette pièce",
			help_text="Adresse spécifique à laquelle le candidat doit envoyer \
cette pièce justificative")

	class Meta:
		constraints = [
			models.CheckConstraint(check = ~models.Q(etablissement__isnull = True, formation__isnull = True),
			name='formation_ou_etablissement_obligatoire'),
			models.CheckConstraint(check = models.Q(etablissement__isnull = True)|models.Q(formation__isnull = True),
			name='formation_ou_etablissement_exclusifs'),
		]

	def __str__(self):
		return self.nom

	@classmethod
	def obligatoire(cls, formation):
		return cls.objects.filter(modalite = cls.MODALITE_OBLIGATOIRE).filter(
			models.Q(etablissement = formation.etablissement)|models.Q(formation = formation))

	@property
	def email(self):
		return next((email for email in [
			self.email_specifique,
			self.formation.email_pieces_justificatives if self.formation else "",
			self.etablissement.email_pieces_justificatives if self.etablissement else "",
			self.formation.email if self.formation else "",
			self.etablissement.email if self.etablissement else ""
			] if email))

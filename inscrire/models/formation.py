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
import ast
from operator import or_
from functools import reduce

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.functional import cached_property

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
			if not fiche._meta.model_name in ('fichepiecejustificative', 'fichepiecejustificativesuivi'):
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
	email_technique = models.EmailField(verbose_name="email à contacter en cas de problème technique",
			help_text="Adresse à contacter en cas de problème technique",
			blank = True, null = False, default = "")
	inscriptions = models.BooleanField(default=False,
			help_text="Indique s'il s'agit d'un établissement dont le "
			"site actuel gère les inscriptions")
	commune = models.ForeignKey('Commune', on_delete=models.SET_NULL,
			blank=True, null=True)
	adresse = models.TextField(default = "")
	photo_size_max = models.PositiveSmallIntegerField(default = 200,
		help_text = "Poids maximal des photos d'identités en ko.")
	photo_largeur = models.PositiveSmallIntegerField(default = 35,
		help_text = "Largeur de la photo d'identité; seul le ratio hauteur/largeur est pris en compte.")
	photo_hauteur = models.PositiveSmallIntegerField(default = 45,
		help_text = "Hauteur de la photo d'identité; seul le ratio hauteur/largeur est pris en compte.")
	tolerance_ratio = models.PositiveSmallIntegerField(default = 10,
		help_text = "Pourcentage de tolérance sur le ratio hauteur/largeur.")

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

	@cached_property
	def candidats(self):
		from .parcoursup import Voeu
		return Candidat.objects.filter(
				voeu__formation__etablissement=self,
				voeu__etat__in=(Voeu.ETAT_ACCEPTE_AUTRES,
					Voeu.ETAT_ACCEPTE_DEFINITIF))

	@cached_property
	def types_fiches_a_valider_candidats(self):
		"""liste des types de fiches à valider par les candidats"""
		from .fiches import all_fiche_validation_candidat
		return [fiche for fiche in all_fiche_validation_candidat if ContentType.objects.get_for_model(fiche) in self.fiches.all()]

	@cached_property
	def fiches_a_valider_candidats(self):
		"""listes des fiches à valider par les candidats"""
		from .fiches import Fiche, all_fiche
		fiches = Fiche.objects.all()
		for type_fiche in all_fiche:
			if not type_fiche in self.types_fiches_a_valider_candidats:
				fiches = fiches.not_instance_of(type_fiche)
		return fiches

	@cached_property
	def types_fiches_a_valider_lycee(self):
		"""liste des types de fiches à valider par les candidats ou l"établissement"""
		from .fiches import all_fiche
		return [fiche for fiche in all_fiche if ContentType.objects.get_for_model(fiche) in self.fiches.all()]


	@cached_property
	def fiches_a_valider_lycee(self):
		"""listes des fiches à valider par les candidats"""
		from .fiches import Fiche, all_fiche
		fiches = Fiche.objects.all()
		for type_fiche in all_fiche:
			if not type_fiche in self.types_fiches_a_valider_lycee:
				fiches = fiches.not_instance_of(type_fiche)
		return fiches

	@cached_property
	def fiches_edition_candidats(self):
		"""Queryset des fiches de l'établissement que les candidats
		doivent compléter et non complètes"""
		from .fiches import Fiche
		return self.fiches_a_valider_candidats.filter(reduce(or_,
			[models.Q(**{"{}__etat".format(type_fiche._meta.model_name):Fiche.ETAT_EDITION})
				for type_fiche in self.types_fiches_a_valider_candidats]))

	@cached_property
	def fiches_edition_lycee(self):
		"""Queryset des fiches non complètes"""
		return self.fiches_a_valider_lycee.filter(reduce(or_,
			[models.Q(**{"{}__etat".format(type_fiche._meta.model_name):Fiche.ETAT_EDITION})
				for type_fiche in self.types_fiches_a_valider_lycee]))

	@cached_property
	def fiches_terminees_lycee(self):
		"""Queryset des fiches terminées"""
		return self.fiches_a_valider_lycee.filter(reduce(or_,
			[models.Q(**{"{}__etat".format(fiche._meta.model_name):Fiche.ETAT_TERMINEE})
				for fiche in self.types_fiches_a_valider_lycee]))

	@cached_property
	def fiches_non_terminees_lycee(self):
		"""Queryset des fiches non terminées"""
		from .fiches import Fiche
		return self.fiches_a_valider_lycee.exclude(reduce(or_,
			[models.Q(**{"{}__etat".format(fiche._meta.model_name):Fiche.ETAT_TERMINEE})
				for fiche in self.types_fiches_a_valider_lycee]))

	def candidats_etat_edition(self):
		"""Candidats dont au moins une fiche à valider
		par leurs soins est en etat édition"""
		return self.candidats.filter(fiche__in=self.fiches_edition_candidats).distinct()

	def candidats_etat_complet(self):
		"""Candidats dont
		- aucune fiche qu'il doit valider n'est en etat édition
		- au moins une fiche (editable par le candidat ou non) n'est pas terminée."""
		return self.candidats.exclude(fiche__in=self.fiches_edition_candidats).filter(
			fiche__in=self.fiches_non_terminees_lycee).distinct()

	def candidats_etat_termine(self):
		"""Candidats dont toutes les fiches sont dans l'état terminé"""
		return self.candidats.exclude(models.Q(fiche__in=self.fiches_non_terminees_lycee)).distinct()

	def candidats_etat_demission(self):
		from .parcoursup import Voeu
		voeux_demissionnes=Voeu.objects.filter(formation__etablissement=self, etat=Voeu.ETAT_REFUSE)
		return Candidat.objects.filter(voeu__in = voeux_demissionnes)

	def confirme_inscription_administrative(self):
		"""Confirme à Parcoursup l'inscription administrative des candidats
		de l'établissement dans l'état terminé"""
		parcoursupuser = self.parcoursupuser
		for candidat in self.candidats_etat_termine().filter(
			inscription_administrative_confirmee=False):
			reponse=parcoursupuser.set_inscription(candidat)
			if reponse.status_code==200:
				str_reponse=reponse.content.decode("UTF-8")
				dict_reponse=ast.literal_eval(str_reponse)
				if dict_reponse['retour']=="OK":
					candidat.inscription_administrative_confirmee=True
					candidat.inscription_administrative_message=dict_reponse['message']
					candidat.save()


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
	sujet_email_pieces_justificatives = models.CharField(max_length = 100, default = "", blank = True)
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

	@property
	def email_defaut(self):
		return self.email or self.etablissement.email

	@property
	def email_pj(self):
		return self.email_pieces_justificatives or self.etablissement.email_pieces_justificatives or self.email or self.etablissement.email

	def candidats(self):
		from .parcoursup import Voeu
		return Candidat.objects.filter(
				voeu__formation=self,
				voeu__etat__in=(Voeu.ETAT_ACCEPTE_AUTRES,
					Voeu.ETAT_ACCEPTE_DEFINITIF))

	def candidats_etat_edition(self):
		"""Candidats dont au moins une fiche à valider
		par leurs soins est en etat édition"""
		return self.candidats().filter(fiche__in=self.etablissement.fiches_edition_candidats).distinct()

	def candidats_etat_complet(self):
		"""Candidats dont
		- aucune fiche qu'il doit valider n'est en etat édition
		- au moins une fiche (editable par le candidat ou non) n'est pas terminée."""
		return self.candidats().exclude(fiche__in=self.etablissement.fiches_edition_candidats).filter(
			fiche__in=self.etablissement.fiches_non_terminees_lycee).distinct()

	def candidats_etat_termine(self):
		"""Candidats dont toutes les fiches sont dans l'état terminé"""
		return self.candidats().exclude(models.Q(fiche__in=self.etablissement.fiches_non_terminees_lycee)).distinct()

	def candidats_etat_demission(self):
		from .parcoursup import Voeu
		voeux_demissionnes=Voeu.objects.filter(formation=self, etat=Voeu.ETAT_REFUSE)
		return Candidat.objects.filter(voeu__in = voeux_demissionnes)

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
		ordering = ['libelle_edition']

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
	detail = models.CharField(max_length = 50, default = "", blank = True,
			help_text = "Précision éventuelle (débutant, continuant, ...)")
	inscriptions = models.BooleanField(default=False,
			help_text="Indique si l'option est présentée aux candidats "
			"afin qu'ils la choisissent lors de l'inscription.")

	class Meta:
		verbose_name = "option MEF"
		verbose_name_plural = "options MEF"
		ordering = ['rang', 'matiere']

	def __str__(self):
		if self.modalite == self.MODALITE_OBLIGATOIRE:
			return "{} {} ({}, rang {})".format(self.matiere, self.detail,
					self.get_modalite_display(), self.rang)
		else:
			return "{} {} ({})".format(self.matiere, self.detail,
					self.get_modalite_display())


class PieceJustificative(models.Model):
	"""Pièce que le candidat peut ou doit envoyer. Les précisions éventuelles
	seront apportées au candidat via l'entête de chaque fiche (modèle EnteteFiche)"""
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


	@classmethod
	def obligatoire(cls, formation):
		return cls.objects.filter(modalite = cls.MODALITE_OBLIGATOIRE).filter(
			models.Q(etablissement = formation.etablissement)|models.Q(formation = formation))

	class Meta:
		constraints = [
			models.CheckConstraint(check = ~models.Q(etablissement__isnull = True, formation__isnull = True),
			name='formation_ou_etablissement_obligatoire'),
			models.CheckConstraint(check = models.Q(etablissement__isnull = True)|models.Q(formation__isnull = True),
			name='formation_ou_etablissement_exclusifs'),
		]

	def __str__(self):
		return self.nom

class Classement(models.Model):
	"""Mémorise le classement envoyé à Parcoursup en vue de
	l'inclure dans le fichier final pour faciliter la composition
	des classes"""
	formation=models.ForeignKey(Formation, on_delete=models.CASCADE)
	dossier_parcoursup=models.IntegerField()
	classement=models.PositiveSmallIntegerField()

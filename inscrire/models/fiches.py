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

"""
Informations d'inscription des candidats dans une formation.

Les informations sont regroupées par fiches. Chaque fiche regroupe les
informations spécifiques à un service donné.
"""

from django.db import models
from polymorphic.models import PolymorphicModel
import localflavor.generic.models as lfmodels

from .personnes import Candidat, Commune, Pays
from .formation import MefOption, Formation, Etablissement

class Fiche(PolymorphicModel):
	"""
	Classe de base pour une fiche d'inscription.

	Grâce à django-polymorphic, les requêtes sur ce modèle renvoient
	directement des instances des bonnes sous-classes, ce qui permet de
	surcharger naturellement les méthodes.

	Le champ FICHE_LABEL est un libellé utilisable sur l'interface
	utilisateur.
	"""
	FICHE_LABEL = "Données d'inscription"
	valide = models.BooleanField()
	candidat = models.ForeignKey(Candidat, on_delete=models.CASCADE)

	ETAT_EDITION = 1
	ETAT_CONFIRMEE = 2
	ETAT_TERMINEE = 3
	ETAT_ANNULEE = 4
	ETAT_CHOICES = (
		(ETAT_EDITION, "fiche à compléter"),
		(ETAT_CONFIRMEE, "fiche confirmée"),
		(ETAT_TERMINEE, "validée par le gestionnaire"),
		(ETAT_ANNULEE, "annulée")
	)
	etat = models.PositiveSmallIntegerField(verbose_name="état",
			choices=ETAT_CHOICES, default=ETAT_EDITION)

	@classmethod
	def fiche_applicable(kls, voeu):
		"""
		Méthode qui indique si une fiche est applicable à un vœu donné.

		Cette méthode renvoie un booléen si cette fiche est demandée
		pour l'inscription d'un candidat étant donné le vœu qu'il a
		accepté. L'implémentation de base renvoie toujours True. Cette
		méthode devrait être surchargée.
		"""
		return True

class FicheIdentite(Fiche):
	"""
	Informations concernant l'identité du candidat
	"""
	FICHE_LABEL = "Identité"
	photo = models.ImageField(upload_to=lambda instance, filename:
			"photo/{psup}/{filename}".format(
				psup=instance.candidat.numero_parcoursup,
				filename=filename))
	piece_identite = models.FileField(
			upload_to=lambda instance, filename: "piece_identite/{psup}/{filename}".format(
				psup=instance.candidat.numero_parcoursup,
				filename=filename))
	commune_naissance = models.ForeignKey(Commune,
			on_delete=models.PROTECT)
	commune_naissance_etranger = models.CharField(max_length=200)
	pays_naissance = models.ForeignKey(Pays, on_delete=models.PROTECT)

class FicheScolariteAnterieure(Fiche):
	"""
	Scolarité antérieure
	"""
	FICHE_LABEL = "Scolarité antérieure"
	etablissement = models.ForeignKey(Etablissement,
			on_delete=models.PROTECT)
	classe_terminale = models.CharField(max_length=20,
			verbose_name="classe de terminale suivie")
	specialite_terminale = models.CharField(max_length=100,
			verbose_name="spécialité en terminale")
	autre_formation = models.CharField(max_length=200,
			verbose_name="autre formation")

class BulletinScolaire(models.Model):
	"""
	Copie d'un bulletin scolaire
	"""
	fiche_scolarite = models.ForeignKey(FicheScolariteAnterieure,
			on_delete=models.CASCADE)

	CLASSE_PREMIERE = 1
	CLASSE_TERMINALE = 2
	CLASSE_CHOICES = (
			(CLASSE_PREMIERE, "bulletin de première"),
			(CLASSE_TERMINALE, "bulletin de terminale"),
		)
	classe = models.PositiveSmallIntegerField(choices=CLASSE_CHOICES)

	bulletin = models.FileField(
			upload_to=lambda instance, filename: "bulletin/{psup}/{filename}".format(
				psup=instance.candidat.numero_parcoursup,
				filename=filename))

class FicheBourse(Fiche):
	"""
	Bourse du supérieur
	"""
	FICHE_LABEL = "Bourse du supérieur"
	boursier = models.BooleanField()
	echelon = models.PositiveSmallIntegerField(verbose_name="échelon",
			blank=True, null=True)
	enfants_charge = models.PositiveSmallIntegerField(
			verbose_name="nombre d'enfants à charge (y compris l'étudiant)",
			default=1)
	enfants_secondaire = models.PositiveSmallIntegerField(
			verbose_name="nombre d'enfants en lycée ou en collège")
	enfants_etablissement = models.PositiveSmallIntegerField(
			verbose_name="nombre d'enfants dans l'établissement")
	attribution_bourse = models.FileField(
			verbose_name="copie de l'attestation conditionnelle de bourse",
			upload_to=lambda instance, filename: "bourse_acb/{psup}/{filename}".format(
				psup=instance.candidat.numero_parcoursup,
				filename=filename))

class FicheReglement(Fiche):
	"""
	Règlement intérieur
	"""
	FICHE_LABEL = "Règlement intérieur"
	signature_reglement = models.DateTimeField(
			verbose_name="signature du règlement intérieur")
	autorisation_parents_eleves = models.BooleanField()

class FicheScolarite(Fiche):
	"""
	Choix des options dans la formation
	"""
	FICHE_LABEL = "Choix des options"
	formation = models.ForeignKey(Formation, on_delete=models.CASCADE)
	options = models.ManyToManyField(MefOption)

class FicheHebergement(Fiche):
	"""
	Choix du mode d'hébergement
	"""
	FICHE_LABEL = "Mode d'hébergement"

	REGIME_EXTERNE = 0
	REGIME_DEMIPENSIONNAIRE = 1
	REGIME_INTERNEEXTERNE = 2
	REGIME_INTERNE = 3
	REGIME_CHOICES = (
		(REGIME_EXTERNE, "externe"),
		(REGIME_DEMIPENSIONNAIRE, "demi-pensionnaire"),
		(REGIME_INTERNEEXTERNE, "interne externé"),
		(REGIME_INTERNE, "interne"),
	)
	regime = models.PositiveSmallIntegerField(verbose_name="régime",
			choices=REGIME_CHOICES)
	iban = lfmodels.IBANField(include_countries=('FR',))
	bic = lfmodels.BICField()
	titulaire_compte = models.CharField(max_length=200)

class FicheInternat(Fiche):
	"""
	Renseignements spécifiques à l'internat
	"""
	FICHE_LABEL = "Internat"

	message = models.TextField(verbose_name="demandes particulières",
			default="", blank=True, null=False)

	@classmethod
	def fiche_applicable(kls, voeu):
		return voeu.internat

class FicheCesure(Fiche):
	"""
	Données à remplir en cas de demande de césure
	"""
	FICHE_LABEL = "Demande de césure"

	@classmethod
	def fiche_applicable(kls, voeu):
		return voeu.cesure

# Liste de toutes les fiches à essayer lors de la création d'un dossier.
all_fiche = [FicheIdentite, FicheScolarite, FicheHebergement,
		FicheInternat, FicheCesure, FicheReglement]

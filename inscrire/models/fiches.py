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

from .personnes import Candidat
from .formation import MefOption, Formation

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

class FicheIdentite(Fiche):
	"""
	Informations concernant l'identité du candidat
	"""
	FICHE_LABEL = "Identité"
	photo = models.ImageField(upload_to=lambda instance, filename:
			"photo/{psup}/{filename}".format(
				psup=instance.candidat.numero_parcoursup,
				filename=filename))

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
	message = models.TextField(verbose_name="demandes particulières",
			default="", blank=True, null=False)

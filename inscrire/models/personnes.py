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
	last_name = models.CharField(max_length=100)
	first_name = models.CharField(verbose_name="prénom", max_length=100)
	adresse = models.TextField()
	telephone = models.CharField(verbose_name="téléphone",
			max_length=20, blank=True, null=False)
	telephone_mobile = models.CharField(verbose_name="téléphone mobile",
			max_length=20, blank=True, null=False)
	adresse = models.TextField(blank=True, null=False)

	def __str__(self):
		return "{} {}".format(self.first_name, self.last_name)

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

class ResponsableLegal(Personne):
	"""
	Coordonnées du responsable légal d'un candidat
	"""
	candidat = models.ForeignKey(Candidat, related_name='responsables',
			on_delete=models.CASCADE)

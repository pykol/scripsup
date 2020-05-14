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
Formulaires gérant l'édition des fiches d'inscription

Le choix du formulaire utilisé par l'interface publique se fait grâce
aux dictionnaires candidat_form et gestionnaire_form qui à chaque modèle
de fiche associent la classe de formulaire à utiliser.
"""

from django import forms

from inscrire.models import fiches

class IdentiteForm(forms.ModelForm):
	prefix = 'fiche-identite'
	class Meta:
		model = fiches.FicheIdentite
		fields = ['photo', 'piece_identite', 'commune_naissance',
				'commune_naissance_etranger', 'pays_naissance']

class ScolariteAnterieureForm(forms.ModelForm):
	prefix = 'fiche-scolariteanterieure'
	class Meta:
		model = fiches.FicheScolariteAnterieure
		fields = ['etablissement', 'classe_terminale',
				'specialite_terminale', 'autre_formation']
		# TODO gestion des bulletins

class BourseForm(forms.ModelForm):
	prefix = 'fiche-bourse'
	class Meta:
		model = fiches.FicheBourse
		fields = ['boursier', 'echelon', 'enfants_charge',
				'enfants_secondaire', 'enfants_etablissement',
				'attribution_bourse']

class ReglementForm(forms.ModelForm):
	prefix = 'fiche-reglement'
	class Meta:
		model = fiches.FicheReglement
		fields = ['signature_reglement', 'autorisation_parents_eleeves']

# Dictionnaire qui à chaque modèle de fiche associe le formulaire
# d'édition qui doit être présenté aux candidats.
candidat_form = {
		fiches.FicheIdentite: IdentiteForm,
		fiches.FicheScolariteAnterieure: ScolariteAnterieureForm,
		fiches.FicheBourse: BourseForm,
		fiches.FicheReglement: ReglementForm,
	}

# Dictionnaire qui à chaque modèle de fiche associe le formulaire
# d'édition qui doit être présenté aux gestionnaires du lycée.
gestionnaire_form = {
	}

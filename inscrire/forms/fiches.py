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
from django.core.exceptions import ValidationError
from django.utils import timezone
from dal import autocomplete

from inscrire.models import fiches

class FicheValiderMixin:
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if self.instance.etat != self.instance.ETAT_EDITION:
			for field in self.fields.values():
				field.disabled = True

	def save(self, commit=True):
		instance = super().save(commit=False)
		instance.valider()
		if commit:
			instance.save()
		return instance

class IdentiteForm(FicheValiderMixin, forms.ModelForm):
	prefix = 'fiche-identite'
	class Meta:
		model = fiches.FicheIdentite
		fields = ['photo', 'piece_identite', 'commune_naissance',
				'commune_naissance_etranger', 'pays_naissance']
		widgets = {
			'commune_naissance': autocomplete.ModelSelect2(url='autocomplete-commune'),
			'pays_naissance': autocomplete.ModelSelect2(url='autocomplete-pays'),
		}
		labels = {
			'commune_naissance': "Commune de naissance",
			'commune_naissance_etranger': "Commune de naissance (étranger)",
			'piece_identite': "Copie de votre pièce d'identité",
			'photo': "Photo d'identité (de face, sur fond blanc)",
			'pays_naissance': "Pays de naissance",
		}
		help_texts = {
			'commune_naissance_etranger': "Si votre commune de naissance "
				"n'est pas une commune française, remplissez ce champ en "
				"indiquant le nom de la commune.",
			'commune_naissance': "Si votre commune de naissance est en "
				"France, complétez ce champ.",
			'pays_naissance': "Sélectionnez votre pays de naissance "
				"parmi les choix proposés dans la liste. Vous pouvez "
				"taper les premières lettres du nom pour trouver plus "
				"rapidement le pays."
		}

class ScolariteAnterieureForm(FicheValiderMixin, forms.ModelForm):
	prefix = 'fiche-scolariteanterieure'
	class Meta:
		model = fiches.FicheScolariteAnterieure
		fields = ['etablissement', 'classe_terminale',
				'specialite_terminale', 'autre_formation']
		# TODO gestion des bulletins
		widgets = {
			'etablissement': autocomplete.ModelSelect2(url='autocomplete-etablissement'),
		}

class BourseForm(FicheValiderMixin, forms.ModelForm):
	prefix = 'fiche-bourse'
	class Meta:
		model = fiches.FicheBourse
		fields = ['enfants_secondaire', 'enfants_etablissement',
				'boursier', 'echelon', 'attribution_bourse']
		labels = {
			'boursier': "Êtes-vous boursier de l'enseignement "
				"supérieur ?",
		}
		help_texts = {
			'boursier' : "Si vous êtes boursier, nous vous demandons "
				"également le rang d'attribution de votre bourse et "
				"de nous faire parvenir en pièce jointe une copie de "
				"votre attribution conditionnelle de bourse."
		}

class ReglementForm(FicheValiderMixin, forms.ModelForm):
	prefix = 'fiche-reglement'
	acceptation_reglement = forms.BooleanField(required=False,
			initial=False,
			label="Je confirme avoir lu le règlement "
			"intérieur et j'en accepte les termes")
	class Meta:
		model = fiches.FicheReglement
		fields = ['autorisation_parents_eleves']
		labels = {
			'autorisation_parents_eleves': "J'autorise le lycée à "
			"communiquer mes coordonnées aux associations de parents "
			"d'élèves"
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['acceptation_reglement'].initial = self.instance.signature_reglement is not None

	def save(self, commit=True):
		fiche = super().save(commit=False)
		if fiche.signature_reglement is None and \
				self.cleaned_data['acceptation_reglement']:
			fiche.signature_reglement = timezone.now()
		if fiche.signature_reglement is not None and \
				not self.cleaned_data['acceptation_reglement']:
			fiche.signature_reglement = None

		fiche.valider()

		if commit:
			fiche.save()
		return fiche

class HebergementForm(FicheValiderMixin, forms.ModelForm):
	prefix = 'fiche-hebergement'
	class Meta:
		model = fiches.FicheHebergement
		fields = ['regime', 'iban', 'bic', 'titulaire_compte']
		labels = {
			'regime': "Régime",
			'iban': "IBAN",
			'bic': "BIC",
			'titulaire_compte': 'Titulaire du compte',
		}
		help_texts = {
			'regime': "Merci de choisir le mode d'hébergement dont "
			"vous souhaitez bénéficier. Le choix de l'internat n'est "
			"possible que si cette proposition vous a été faite par "
			"Parcoursup."
		}

	def clean_regime(self):
		if self.cleaned_data['regime'] == fiches.FicheHebergement.REGIME_INTERNE and \
				not self.instance.candidat.voeu_actuel.internat:
			raise ValidationError("L'internat ne vous a pas été proposé "
				"sur Parcoursup. Vous ne pouvez pas sélectionner ici "
				"ce mode d'hébergement", code='internat')
		if self.cleaned_data['regime'] != fiches.FicheHebergement.REGIME_INTERNE and \
				self.instance.candidat.voeu_actuel.internat:
			raise ValidationError("Le vœu que vous avez accepté sur "
				"Parcoursup est un vœu avec internat. Vous ne pouvez "
				"pas changer de mode d'hébergement. Si vous souhaitez "
				"renoncer à l'internat, contactez directement "
				"l'établissement.", code='internat')
		return self.cleaned_data['regime']


# Dictionnaire qui à chaque modèle de fiche associe le formulaire
# d'édition qui doit être présenté aux candidats.
candidat_form = {
		fiches.FicheIdentite: IdentiteForm,
		fiches.FicheScolariteAnterieure: ScolariteAnterieureForm,
		fiches.FicheBourse: BourseForm,
		fiches.FicheReglement: ReglementForm,
		fiches.FicheHebergement: HebergementForm,
	}

# Dictionnaire qui à chaque modèle de fiche associe le formulaire
# d'édition qui doit être présenté aux gestionnaires du lycée.
gestionnaire_form = {
	}

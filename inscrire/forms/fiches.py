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
from django.forms.utils import ErrorList
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from dal import autocomplete

from inscrire.models import fiches, ResponsableLegal, Candidat
from inscrire.models import MefOption

class FicheValiderMixin:
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if self.instance.etat != self.instance.ETAT_EDITION:
			for field in self.fields.values():
				field.disabled = True

	def save(self, commit=True):
		if commit:
			instance = super().save(commit=True)
			instance.valider()
			instance.save()
		else:
			instance = super().save(commit=False)

		return instance

class IdentiteFicheForm(FicheValiderMixin, forms.ModelForm):
	prefix = 'fiche-identite'
	class Meta:
		model = fiches.FicheIdentite
		fields = ['photo', 'piece_identite', 'commune_naissance',
				'commune_naissance_etranger', 'pays_naissance',
				'adresse', 'ville', 'pays', 'telephone']
		widgets = {
			'commune_naissance': autocomplete.ModelSelect2(url='autocomplete-commune'),
			'pays_naissance': autocomplete.ModelSelect2(url='autocomplete-pays'),
			'ville': autocomplete.ModelSelect2(url='autocomplete-commune'),
			'pays': autocomplete.ModelSelect2(url='autocomplete-pays'),
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
				"rapidement le pays.",
			'ville': "Si votre commune de résidence est en "
				"France, complétez ce champ.",
			'pays': "Sélectionnez votre pays de résidence "
				"parmi les choix proposés dans la liste. Vous pouvez "
				"taper les premières lettres du nom pour trouver plus "
				"rapidement le pays."
		}

ResponsablesForm = forms.inlineformset_factory(
		Candidat, ResponsableLegal,
		fields=('genre', 'last_name', 'first_name',
			'lien', 'lien_precision',
			'adresse', 'telephone', 'telephone_mobile',
			'email',
			'profession'),
		extra=1, max_num=3, can_delete=True)

class IdentiteForm(FicheValiderMixin):
	form_classes = [IdentiteFicheForm, ResponsablesForm]

	def __init__(self, instance=None, data=None, files=None, auto_id='id_%s', prefix=None,
			initial=None, error_class=ErrorList, form_kwargs=None):
		self.instance = instance
		self.is_bound = data is not None or files is not None
		self.prefix = prefix or self.get_default_prefix()
		self.auto_id = auto_id
		self.data = data or {}
		self.files = files or {}
		self.initial = initial
		self.form_kwargs = form_kwargs or {}
		self.error_class = error_class
		self._errors = None
		self._non_form_errors = None

	def __str__(self):
		return self.as_table()

	def __iter__(self):
		"""Yield the forms in the order they should be rendered."""
		return iter(self.forms)

	def __getitem__(self, index):
		"""Return the form at the given index, based on the rendering order."""
		return self.forms[index]

	def __len__(self):
		return len(self.forms)

	def __bool__(self):
		"""
		Return True since all formsets have a management form which is not
		included in the length.
		"""
		return True

	@cached_property
	def forms(self):
		"""Instantiate forms at first property access."""
		return [
			self._construct_form(i)
			for i in range(len(self.form_classes))
		]

	def _construct_form(self, i, **kwargs):
		"""Instantiate and return the i-th form instance in a formset."""
		defaults = {
			'auto_id': self.auto_id,
			'prefix': self.add_prefix(i),
			'error_class': self.error_class,
			'instance': self.instance if i == 0 else self.instance.candidat,
		}
		if self.is_bound:
			defaults['data'] = self.data
			defaults['files'] = self.files
		if self.initial and 'initial' not in kwargs:
			try:
				defaults['initial'] = self.initial[i]
			except IndexError:
				pass
		defaults.update(kwargs)
		form = self.form_classes[i](**defaults)
		return form

	@property
	def cleaned_data(self):
		"""
		Return a list of form.cleaned_data dicts for every form in self.forms.
		"""
		if not self.is_valid():
			raise AttributeError("'%s' object has no attribute 'cleaned_data'" % self.__class__.__name__)
		return [form.cleaned_data for form in self.forms]

	def get_default_prefix(cls):
		return 'fiche-identite'

	def non_form_errors(self):
		"""
		Return an ErrorList of errors that aren't associated with a particular
		form -- i.e., from formset.clean(). Return an empty ErrorList if there
		are none.
		"""
		if self._non_form_errors is None:
			self.full_clean()
		return self._non_form_errors

	@property
	def errors(self):
		"""Return a list of form.errors for every form in self.forms."""
		if self._errors is None:
			self.full_clean()
		return self._errors

	def total_error_count(self):
		"""Return the number of errors across all forms in the formset."""
		return len(self.non_form_errors()) +\
			sum(len(form_errors) for form_errors in self.errors)

	def is_valid(self):
		"""Return True if every form in self.forms is valid."""
		if not self.is_bound:
			return False
		# We loop over every form.errors here rather than short circuiting on the
		# first failure to make sure validation gets triggered for every form.
		forms_valid = True
		# This triggers a full clean.
		self.errors
		for form in self:
			forms_valid &= form.is_valid()
		return forms_valid and not self.non_form_errors()

	def full_clean(self):
		"""
		Clean all of self.data and populate self._errors and
		self._non_form_errors.
		"""
		self._errors = []
		self._non_form_errors = self.error_class()
		empty_forms_count = 0

		if not self.is_bound:  # Stop further processing.
			return
		for form in self:
			self._errors.append(form.errors)
		try:
			# Give self.clean() a chance to do cross-form validation.
			self.clean()
		except ValidationError as e:
			self._non_form_errors = self.error_class(e.error_list)

	def clean(self):
		"""
		Hook for doing any extra formset-wide cleaning after Form.clean() has
		been called on every form. Any ValidationError raised by this method
		will not be associated with a particular form; it will be accessible
		via formset.non_form_errors()
		"""
		pass

	def has_changed(self):
		"""Return True if data in any form differs from initial."""
		return any(form.has_changed() for form in self)

	def add_prefix(self, index):
		return '%s-%s' % (self.prefix, index)

	def is_multipart(self):
		"""
		Return True if the formset needs to be multipart, i.e. it
		has FileInput, or False otherwise.
		"""
		return all(form.is_multipart() for form in self)

	@property
	def media(self):
		return mark_safe(''.join(str(form.media) for form in self))

	def as_table(self):
		"Return this formset rendered as HTML <tr>s -- excluding the <table></table>."
		# XXX: there is no semantic division between forms here, there
		# probably should be. It might make sense to render each form as a
		# table row with each field as a td.
		return mark_safe(' '.join(form.as_table() for form in self))

	def as_p(self):
		"Return this formset rendered as HTML <p>s."
		return mark_safe(' '.join(form.as_p() for form in self))

	def as_ul(self):
		"Return this formset rendered as HTML <li>s."
		return mark_safe(' '.join(form.as_ul() for form in self))

	def save(self, commit=True):
		for form in self:
			form.save(commit)

class ScolariteAnterieureBaseForm(FicheValiderMixin, forms.ModelForm):
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

class ScolariteForm(FicheValiderMixin, forms.ModelForm):
	prefix = 'fiche-scolarite'
	class Meta:
		model = fiches.FicheScolarite
		fields = ['options',]
		widgets = {
			'options': forms.CheckboxSelectMultiple,
		}

	def options_qs(self):
		return MefOption.objects.filter(
			formation=self.instance.candidat.voeu_actuel.formation,
			inscriptions=True)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['options'].queryset = self.options_qs().order_by(
			'modalite', 'rang', 'matiere__libelle_edition')

	def clean_options(self):
		errors = []
		rangs_choisis = {}
		for option in self.cleaned_data['options']:
			if option.rang in rangs_choisis and \
				option.modalite == MefOption.MODALITE_OBLIGATOIRE:
				errors.append(ValidationError("Vous ne devez choisir "
					"qu'une seule option parmi les choix possibles "
					"pour le rang %(rang)d.",
					params={'rang': option.rang},
					code='rang-multiple-options'))
			else:
				rangs_choisis[option.rang] = option

		if errors:
			raise ValidationError(errors)

		return self.cleaned_data['options']

ScolariteBulletinForm = forms.inlineformset_factory(
		fiches.FicheScolariteAnterieure, fiches.BulletinScolaire,
		fields=('classe', 'bulletin'), extra=5, max_num=10,
		can_delete=True)
#TODO créer un form dédié pour éditer les bulletins, dérivant de
#FicheValiderMixin

class ScolariteAnterieureForm:
	form_classes = [ScolariteAnterieureBaseForm, ScolariteBulletinForm]

	def __init__(self, instance=None, data=None, files=None, auto_id='id_%s', prefix=None,
			initial=None, error_class=ErrorList, form_kwargs=None):
		self.instance = instance
		self.is_bound = data is not None or files is not None
		self.prefix = prefix or self.get_default_prefix()
		self.auto_id = auto_id
		self.data = data or {}
		self.files = files or {}
		self.initial = initial
		self.form_kwargs = form_kwargs or {}
		self.error_class = error_class
		self._errors = None
		self._non_form_errors = None

	def __str__(self):
		return self.as_table()

	def __iter__(self):
		"""Yield the forms in the order they should be rendered."""
		return iter(self.forms)

	def __getitem__(self, index):
		"""Return the form at the given index, based on the rendering order."""
		return self.forms[index]

	def __len__(self):
		return len(self.forms)

	def __bool__(self):
		"""
		Return True since all formsets have a management form which is not
		included in the length.
		"""
		return True

	@cached_property
	def forms(self):
		"""Instantiate forms at first property access."""
		return [
			self._construct_form(i)
			for i in range(len(self.form_classes))
		]

	def _construct_form(self, i, **kwargs):
		"""Instantiate and return the i-th form instance in a formset."""
		defaults = {
			'auto_id': self.auto_id,
			'prefix': self.add_prefix(i),
			'error_class': self.error_class,
			'instance': self.instance,
		}
		if self.is_bound:
			defaults['data'] = self.data
			defaults['files'] = self.files
		if self.initial and 'initial' not in kwargs:
			try:
				defaults['initial'] = self.initial[i]
			except IndexError:
				pass
		defaults.update(kwargs)
		form = self.form_classes[i](**defaults)
		return form

	@property
	def cleaned_data(self):
		"""
		Return a list of form.cleaned_data dicts for every form in self.forms.
		"""
		if not self.is_valid():
			raise AttributeError("'%s' object has no attribute 'cleaned_data'" % self.__class__.__name__)
		return [form.cleaned_data for form in self.forms]

	def get_default_prefix(cls):
		return 'fiche-scolarite'

	def non_form_errors(self):
		"""
		Return an ErrorList of errors that aren't associated with a particular
		form -- i.e., from formset.clean(). Return an empty ErrorList if there
		are none.
		"""
		if self._non_form_errors is None:
			self.full_clean()
		return self._non_form_errors

	@property
	def errors(self):
		"""Return a list of form.errors for every form in self.forms."""
		if self._errors is None:
			self.full_clean()
		return self._errors

	def total_error_count(self):
		"""Return the number of errors across all forms in the formset."""
		return len(self.non_form_errors()) +\
			sum(len(form_errors) for form_errors in self.errors)

	def is_valid(self):
		"""Return True if every form in self.forms is valid."""
		if not self.is_bound:
			return False
		# We loop over every form.errors here rather than short circuiting on the
		# first failure to make sure validation gets triggered for every form.
		forms_valid = True
		# This triggers a full clean.
		self.errors
		for form in self:
			forms_valid &= form.is_valid()
		return forms_valid and not self.non_form_errors()

	def full_clean(self):
		"""
		Clean all of self.data and populate self._errors and
		self._non_form_errors.
		"""
		self._errors = []
		self._non_form_errors = self.error_class()
		empty_forms_count = 0

		if not self.is_bound:  # Stop further processing.
			return
		for form in self:
			self._errors.append(form.errors)
		try:
			# Give self.clean() a chance to do cross-form validation.
			self.clean()
		except ValidationError as e:
			self._non_form_errors = self.error_class(e.error_list)

	def clean(self):
		"""
		Hook for doing any extra formset-wide cleaning after Form.clean() has
		been called on every form. Any ValidationError raised by this method
		will not be associated with a particular form; it will be accessible
		via formset.non_form_errors()
		"""
		pass

	def has_changed(self):
		"""Return True if data in any form differs from initial."""
		return any(form.has_changed() for form in self)

	def add_prefix(self, index):
		return '%s-%s' % (self.prefix, index)

	def is_multipart(self):
		"""
		Return True if the formset needs to be multipart, i.e. it
		has FileInput, or False otherwise.
		"""
		return all(form.is_multipart() for form in self)

	@property
	def media(self):
		return mark_safe(''.join(str(form.media) for form in self))

	def as_table(self):
		"Return this formset rendered as HTML <tr>s -- excluding the <table></table>."
		# XXX: there is no semantic division between forms here, there
		# probably should be. It might make sense to render each form as a
		# table row with each field as a td.
		return mark_safe(' '.join(form.as_table() for form in self))

	def as_p(self):
		"Return this formset rendered as HTML <p>s."
		return mark_safe(' '.join(form.as_p() for form in self))

	def as_ul(self):
		"Return this formset rendered as HTML <li>s."
		return mark_safe(' '.join(form.as_ul() for form in self))

	def save(self, commit=True):
		for form in self:
			form.save(commit)

# Dictionnaire qui à chaque modèle de fiche associe le formulaire
# d'édition qui doit être présenté aux candidats.
candidat_form = {
		fiches.FicheIdentite: IdentiteForm,
		fiches.FicheScolariteAnterieure: ScolariteAnterieureForm,
		fiches.FicheBourse: BourseForm,
		fiches.FicheReglement: ReglementForm,
		fiches.FicheHebergement: HebergementForm,
		fiches.FicheScolarite: ScolariteForm,
	}

# Dictionnaire qui à chaque modèle de fiche associe le formulaire
# d'édition qui doit être présenté aux gestionnaires du lycée.
gestionnaire_form = {
	}

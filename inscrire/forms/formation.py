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

import codecs
from django import forms

from inscrire.models import Formation
from inscrire.lib.parcoursup_fichiers import parse_export_standard

class ImportParcoursupForm(forms.Form):
	export = forms.FileField()
	formation = forms.ModelChoiceField(
			queryset=Formation.objects.filter(code_parcoursup__isnull=False
				).order_by('etablissement', 'pk'))

	def propositions(self):
		return parse_export_standard(
				codecs.iterdecode(self.cleaned_data['export'],
					'utf-8'),
				self.cleaned_data['formation'].etablissement.pk,
				self.cleaned_data['formation'].code_parcoursup)

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
Formulaires gérant le paramétrage des formations
"""

import zipfile

from django import forms

from inscrire.models import Formation
from inscrire.lib.siecle.fichiers import Nomenclature, Structures

class ImportStructuresForm(forms.Form):
	structures = forms.FileField()
	nomenclature = forms.FileField()

	@staticmethod
	def _open_maybe_zip(source_file):
		try:
			file_zip = zipfile.ZipFile(source_file)
			return file_zip.open(file_zip.namelist()[0])
		except zipfile.BadZipFile:
			source_file.seek(0)
			return source_file

	def lire_structures(self):
		"""
		Renvoie la liste des classes du fichier structures
		"""
		return Structures(self.cleaned_data['structures'])

	def lire_nomenclature(self):
		"""
		Construit la liste des options pour chaque formation
		"""
		return Nomenclature(self.cleaned_data['nomenclature'])

class FormationForm(forms.ModelForm):
	class Meta:
		model = Formation
		fields = ['nom', 'code_parcoursup', 'groupe_parcoursup',
				'etablissement', 'slug', 'code_mef']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.etablissement.queryset = Etablissement.objects.filter(inscriptions=True).order_by('numero_uai')

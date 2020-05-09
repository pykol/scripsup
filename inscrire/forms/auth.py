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
Formulaires gérant l'identification des utilisateurs
"""
from django import forms
from django.core.validators import RegexValidator

from inscrire.models.parcoursup import ParcoursupUser
from inscrire.models import Etablissement

class EnvoiBienvenueForm(forms.Form):
	"""
	Demande de renvoi de l'e-mail de bienvenue à partir du numéro
	Parcoursup
	"""
	etablissement = forms.ModelChoiceField(
			queryset=Etablissement.objects.order_by('numero_uai'),
			label="établissement",
			initial=Etablissement.objects.order_by('numero_uai').first)
	numero_dossier = forms.CharField(max_length=10,
			label="Numéro de dossier Parcoursup",
			validators=[RegexValidator(regex=r'^\d+$',
				message="Le numéro de dossier ne doit contenir que des chiffres")])

	def envoi_bienvenue(self):
		"""
		Envoie un e-mail de bienvenue au candidat qui l'a demandé.
		"""
		try:
			# Synchro Parcoursup
			psup = ParcoursupUser.objects.get(etablissement=self.cleaned_data['etablissement'])
			candidat = psup.get_candidat_admis(self.cleaned_data['numero_dossier'])
			# Envoi du mail
			candidat.email_bienvenue()
		except:
			# Intercepter des erreurs pour signaler au gestionnaire
			pass

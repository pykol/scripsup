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
from inscrire.models import Etablissement, Candidat
from inscrire.lib.parcoursup_rest import ParcoursupError

class EnvoiBienvenueForm(forms.Form):
	"""
	Demande de renvoi de l'e-mail de bienvenue à partir du numéro
	Parcoursup
	"""
	etablissement = forms.ModelChoiceField(
			queryset=Etablissement.objects.filter(inscriptions=True).order_by('numero_uai'),
			label="établissement",
			initial=Etablissement.objects.filter(inscriptions=True).order_by('numero_uai').first)
	numero_dossier = forms.CharField(max_length=10,
			label="Numéro de dossier Parcoursup",
			validators=[RegexValidator(regex=r'^\d+$',
				message="Le numéro de dossier ne doit contenir que des chiffres")])

	def envoi_bienvenue(self, request):
		"""
		Envoie un e-mail de bienvenue au candidat qui l'a demandé.
		"""
		# Synchro Parcoursup
		try:
			psup = ParcoursupUser.objects.get(etablissement=self.cleaned_data['etablissement'])
			candidat = psup.get_candidat_admis(self.cleaned_data['numero_dossier'])
			# Envoi du mail
			candidat.email_bienvenue(request, force=True)
		except ParcoursupError:
			# Pas de discussion avec Parcoursup. On tente quand même
			# l'envoi de l'e-mail de bienvenue.
			try:
				candidat = Candidat.objects.get(
						voeu__formation__etablissement=self.cleaned_data['etablissement'],
						dossier_parcoursup=self.cleaned_data['numero_dossier'])
				candidat.email_bienvenue(request, force=True)
			except Candidat.DoesNotExist:
				pass
		except:
			pass
		# TODO Intercepter des erreurs pour signaler au gestionnaire

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
Vues permettant le paramétrage des formations gérées
"""
from django.views.generic import FormView, UpdateView, View
from django.urls import reverse_lazy
from django.utils.text import slugify

import inscrire.forms.parametrage as param_forms
from .permissions import AccessGestionnaireMixin, AccessDirectionMixin

class ImportStructuresView(AccessDirectionMixin, FormView):
	"""
	Import des formations depuis les fichiers SIECLE Structures et
	Nomenclatures.

	Le fichier Structures permet de créer la liste des classes. Le
	fichier Nomenclatures permet de créer les listes d'options
	disponibles pour chaque formation.
	"""
	template_name = 'parametrage/import_structures.html'
	form_class = param_forms.ImportStructuresForm
	success_url = reverse_lazy('formation_list')

	def form_valid(self, form):
		structures = form.lire_structures()
		nomenclature = form.lire_nomenclature()
		mefs = nomenclature.mefs()

		# On active automatiquement les inscriptions pour
		# l'établissement, puisque l'on dispose désormais de formations
		# connues.
		etablissement = Etablissement.objects.get(numero_uai=nomenclature.parametres()['uai'])
		etablissement.inscriptions = True
		etablissement.save()

		# Création des classes
		for code_mef in structures.mefs():
			# On ignore ce qui n'est pas une classe du supérieur
			if code_mef[0] != '3':
				continue
			# On crée la formation correspondante
			formation, _ = Formation.objects.update_or_create(
					code_mef=code_mef,
					etablissement=etablissement,
					defaults={
						'nom': mefs[code_mef].libelle_long,
						'slug': slugify(mefs[code_mef].formation),
					}
				)

			def get_matiere(matiere):
				matiere_db, _ = MefMatiere.objects.get_or_create(
						code=matiere.code_matiere,
						libelle_court=matiere.libelle_court,
						libelle_long=matiere.libelle_long,
						libelle_edition=matiere.libelle_edition,
					)
				return matiere_db
			# Ajout des options obligatoires
			for option in mefs[code_mef].options_obligatoires:
				MefOption.objects.update_or_create(
						formation=formation,
						modalite=MefOption.MODALITE_OBLIGATOIRE,
						rang=option.rang,
						matiere=get_matiere(option.matiere),
						defaults={})
			# Ajout des options facultatives
			for option in mefs[code_mef].programme:
				if option.modalite_election == 'F':
					MefOption.objects.update_or_create(
							formation=formation,
							modalite=MefOption.MODALITE_FACULTATIVE,
							rang=0,
							matiere=get_matiere(option.matiere),
							defaults={})

		return super().form_valid(form)

class AccesParcoursupView(UpdateView):
	"""
	Paramétrage d'un accès à l'interface synchrone de Parcoursup
	"""
	pass

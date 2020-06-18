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
from django.views.generic.detail import SingleObjectTemplateResponseMixin, \
		SingleObjectMixin
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.db import IntegrityError

import inscrire.forms.parametrage as param_forms
from inscrire.models import Etablissement, Formation, MefMatiere, \
		MefOption, ParcoursupUser
from .permissions import AccessGestionnaireMixin, AccessDirectionMixin, \
		AccessTechniqueMixin

class ImportStructuresView(AccessDirectionMixin, FormView):
	"""
	Import des formations depuis les fichiers SIECLE Structures et
	Nomenclatures.

	Le fichier Structures permet de créer la liste des classes. Le
	fichier Nomenclatures permet de créer les listes d'options
	disponibles pour chaque formation.
	"""
	template_name = 'inscrire/parametrage/import_structures.html'
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
			formation = None
			formation_slug = slugify(mefs[code_mef].formation)
			formation_slug_rang = 0
			while not formation:
				try:
					formation, _ = Formation.objects.update_or_create(
						code_mef=code_mef,
						etablissement=etablissement,
						defaults={
							'nom': mefs[code_mef].libelle_long,
							'slug': formation_slug,
						}
					)
				except IntegrityError:
					# Slug pas forcément unique, on se laisse quelques
					# tentatives.
					formation_slug_rang += 1
					if formation_slug_rang > 10:
						raise IntegrityError
					formation_slug = "{}-{}".format(
							slugify(mefs[code_mef].formation),
							formation_slug_rang)

			def get_matiere(matiere):
				matiere_db, _ = MefMatiere.objects.get_or_create(
						code=matiere.code,
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

class SynchroParcoursupView(AccessGestionnaireMixin, View):
	"""
	Vue qui force la synchronisation de tous les candidats en
	interrogeant Parcoursup.
	"""
	def post(self):
		pass

class ParcoursupCandidatTestView(AccessTechniqueMixin,
		SingleObjectTemplateResponseMixin, SingleObjectMixin, View):
	model = ParcoursupUser
	template_name = 'inscrire/parametrage/parcoursup_test.html'

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		try:
			self.object.envoi_candidat_test()
			self.parcoursup_success = True
		except HttpError:
			self.parcoursup_success = False
			self.parcoursup_error = "Erreur HTTP"
		except ParcoursupError as e:
			self.parcoursup_success = False
			self.parcoursup_error = "Erreur Parcoursup"
		except:
			self.parcoursup_success = False
			self.parcoursup_error = "Erreur inconnue"

		context = self.get_context_data(object=self.object)
		return self.render_to_response(context)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['parcoursup_success'] = self.parcoursup_success
		if not self.parcoursup_success:
			context['parcoursup_error'] = self.parcoursup_error

		return context

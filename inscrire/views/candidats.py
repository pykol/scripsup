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

from collections import namedtuple

from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView, DetailView, UpdateView
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from django.template.loader import select_template

from inscrire.models import ResponsableLegal, Candidat
from inscrire.models.fiches import Fiche, all_fiche
from inscrire.forms.fiches import candidat_form
from .permissions import AccessPersonnelMixin, AccessGestionnaireMixin

class CandidatDetail(AccessPersonnelMixin, DetailView):
	"""
	Affiche les informations personnelles d'un candidat, à destination
	des personnels de l'établissement.
	"""
	model = Candidat

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		context["candidat"] = self.object
		context["nombre_responsables"] = self.object.responsables.count()
		return context

class ResponsableLegal(AccessPersonnelMixin, DetailView):
	"""
	Affiche les informations personnelles d'un responsable légal
	"""
	model = ResponsableLegal
	template_name = "responsablelegal.html"
	context_object_name = "responsablelegal"

class CandidatFicheMixin:
	"""
	Mixin qui ajoute au contexte la liste des fiches d'inscription que
	le candidat doit remplir.
	"""
	def get_fiches(self):
		"""
		Construction de la liste des fiches.

		Ces fiches peuvent être attachées à des formulaires d'édition.
		Chaque formulaire est initialisé, dans le cas d'une requête
		POST, avec les données soumises.
		"""
		# Ajout des fiches applicables
		FicheTpl = namedtuple('FicheTpl', ('fiche', 'form', 'template'))
		fiches = []
		candidat = self.object
		for fiche in candidat.fiche_set.exclude(etat=Fiche.ETAT_ANNULEE):
			try:
				if self.request.method in ('POST', 'PUT'):
					form = candidat_form[type(fiche)](instance=fiche,
							data=self.request.POST,
							files=self.request.FILES)
				else:
					form = candidat_form[type(fiche)](instance=fiche)
			except:
				form = None

			fiches.append(FicheTpl(
				fiche=fiche,
				form=form,
				template=select_template(
					[
						'fiche/{}_candidat.html'.format(fiche._meta.model_name),
						'fiche/fiche_base_candidat.html'
					])
				))

		fiches.sort(key=lambda fiche:
				all_fiche.index(type(fiche.fiche)))
		return fiches

	def get_context_data(self, **kwargs):
		"""
		Ajout des fiches au contexte. Ces fiches sont créées par un
		appel à la méthode get_fiches sauf si elles sont déjà passées en
		paramètre (ce qui se produit par exemple lors d'un POST qui a
		signalé des erreurs de traitement).
		"""
		context = super().get_context_data()
		context['fiches'] = kwargs.get('fiches', self.get_fiches())
		return context

class CandidatUpdate(AccessGestionnaireMixin, CandidatFicheMixin, UpdateView):
	"""
	Permet la modification des informations personnelles par les
	gestionnaires du lycée.
	"""
	model = Candidat
	fields = ['adresse', 'telephone', 'telephone_mobile', 'date_naissance', 'genre']
	template_name = "candidat_update.html"
	success_url = "/candidat"

	def get(self, request, *args, **kwargs):
		return self.render_to_response(self.get_context_data())

	def post(self, request, *args, **kwargs):
		pass

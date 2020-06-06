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

from django.views.generic import ListView, DetailView, View
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import redirect

from inscrire.models import Formation, Candidat, Voeu, MefOption
from .permissions import AccessDirectionMixin
from inscrire.forms.parametrage import OptionActiverFormset, \
		FormationForm

class FormationListView(AccessDirectionMixin, ListView):
	model = Formation

class FormationDetailView(AccessDirectionMixin, DetailView):
	model = Formation

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['candidat_list'] = Candidat.objects.filter(
				voeu__etat__in=(Voeu.ETAT_ACCEPTE_AUTRES,
					Voeu.ETAT_ACCEPTE_DEFINITIF),
				voeu__formation=self.object,
			).order_by('last_name', 'first_name')
		context['formation_form'] = FormationForm(prefix='formation',
				instance=self.object)
		context['option_formset'] = OptionActiverFormset(prefix='options',
				instance=self.object,
				queryset=MefOption.objects.order_by('modalite', 'rang',
					'matiere__libelle_court'))
		return context

class FormationUpdateView(AccessDirectionMixin, SingleObjectMixin, View):
	model = Formation

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		formation_form = FormationForm(data=self.request.POST,
				instance=self.object,
				prefix='formation')
		if formation_form.is_valid():
			formation_form.save()
		option_formset = OptionActiverFormset(prefix='options',
				instance=self.object, data=self.request.POST)
		if option_formset.is_valid():
			option_formset.save()

		return redirect('formation_detail', slug=self.object.slug)

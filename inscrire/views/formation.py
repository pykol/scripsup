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

from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import UserPassesTestMixin

from inscrire.models import Formation, InscrireUser, Candidat, Voeu

class FormationListView(UserPassesTestMixin, ListView):
	model = Formation
	def test_func(self):
		return self.request.user.role == InscrireUser.ROLE_DIRECTION

class FormationDetailView(UserPassesTestMixin, DetailView):
	model = Formation

	def test_func(self):
		return self.request.user.role == InscrireUser.ROLE_DIRECTION

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['candidat_list'] = Candidat.objects.filter(
				voeu__etat__in=(Voeu.ETAT_ACCEPTE_AUTRES,
					Voeu.ETAT_ACCEPTE_DEFINITIF),
				voeu__formation=self.object,
			).order_by('last_name', 'first_name')
		return context

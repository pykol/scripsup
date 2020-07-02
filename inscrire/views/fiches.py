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

from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from inscrire.models import Fiche

class FicheValiderView(SingleObjectMixin, UserPassesTestMixin, View):
	model = Fiche

	def test_func(self):
		"""
		La validation d'une fiche n'est permise que par un gestionnaire
		ou par le candidat lui-même.
		"""
		if not self.request.user.is_authenticated:
			return False
		if self.request.user.est_gestionnaire():
			return True
		return self.get_object().candidat.user == self.request.user

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		if self.object.etat in (Fiche.ETAT_EDITION,
				Fiche.ETAT_CONFIRMEE):
			self.object.etat = Fiche.ETAT_CONFIRMEE
			self.object.save()

			return redirect('home')

	def get(self, request, *args, **kwargs):
		return None

class FicheTraiterView(SingleObjectMixin, UserPassesTestMixin, View):
	model = Fiche

	def test_func(self):
		"""
		La validation d'une fiche n'est permise que par un gestionnaire.
		"""
		return self.request.is_authenticated and self.request.user.est_gestionnaire()

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		if self.object.etat == Fiche.ETAT_CONFIRMEE:
			self.object.etat = Fiche.ETAT_TERMINEE
			self.object.save()

			return redirect('home')

	def get(self, request, *args, **kwargs):
		return None

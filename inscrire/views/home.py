# -*- coding: utf8 -*-

# scripsup - Inscription en ligne en CPGE
# Copyright (c) 2020 Romain Krust
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

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.generic import View, TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin

from inscrire.models import InscrireUser, Candidat
from .candidats import CandidatFicheMixin

class HomeView(AccessMixin, View):
	"""
	Classe qui oriente l'utilisateur vers la vue d'accueil adaptée à son
	rôle.
	"""
	def dispatch(self, request, *args, **kwargs):
		if not request.user.is_authenticated:
			return self.handle_no_permission()
		return {
			InscrireUser.ROLE_DIRECTION: DirectionHomeView,
			InscrireUser.ROLE_SECRETARIAT: SecretariatHomeView,
			InscrireUser.ROLE_PROFESSEUR: ProfesseurHomeView,
			InscrireUser.ROLE_VIESCOLAIRE: VieScolaireHomeView,
			InscrireUser.ROLE_INTENDANCE: IntendanceHomeView,
			InscrireUser.ROLE_ETUDIANT: EtudiantHomeView,
			}.get(request.user.role).as_view()(request, *args, **kwargs)

class DirectionHomeView(TemplateView):
	pass

class SecretariatHomeView(TemplateView):
	pass

class ProfesseurHomeView(TemplateView):
	pass

class VieScolaireHomeView(TemplateView):
	pass

class IntendanceHomeView(TemplateView):
	pass

class EtudiantHomeView(CandidatFicheMixin, DetailView):
	template_name = 'inscrire/home/home_candidat.html'
	model = Candidat

	def get_object(self, queryset=None):
		return self.request.user.candidat

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['voeu'] = self.request.user.candidat.voeu_actuel
		return context

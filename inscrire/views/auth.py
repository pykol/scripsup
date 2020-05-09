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

from django.contrib.auth import views as auth_views
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from inscrire.forms.auth import EnvoiBienvenueForm

class LoginView(auth_views.LoginView):
	"""
	Vue d'identification qui ajoute le formulaire d'interrogation
	Parcoursup par rapport à la vue standard.
	"""
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['bienvenue_form'] = EnvoiBienvenueForm()

class EnvoiBienvenue(FormView):
	"""
	Vue qui interroge Parcoursup et renvoie l'e-mail de bienvenue à un
	candidat.
	"""
	template_name = 'envoi_bienvenue.html'
	form_class = EnvoiBienvenueForm

	def get_success_url(self):
		return reverse('envoi_bienvenue_confirm')

	def form_valid(self, form):
		form.envoi_email()
		return super().form_valid(form)

class EnvoiBienvenueConfirm(TemplateView):
	"""
	Message de confirmation de l'envoi de l'e-mail de bienvenue.
	"""
	template_name = 'envoi_bienvenue_confirm.html'

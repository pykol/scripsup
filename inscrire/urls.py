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

from django.urls import path, include

from inscrire import views

rest_parcoursup_urlpatterns = [
	path('admissionCandidat', views.parcoursup.AdmissionView),
	# Blague de Parcoursup qui ne respectait pas toujours la spec en 2019
	path('admissionCandidat/admissionCandidat', views.parcoursup.AdmissionView),
]

urlpatterns = [
	path('', views.home, name='home'),
	path('parcoursup', include(rest_parcoursup_urlpatterns)),
	path('candidat', views.CandidatDetail.as_view()),
	path('candidat/miseajour/<int:pk>', views.CandidatUpdate.as_view()),
	path('responsablelegal/<int:pk>', views.ResponsableLegal.as_view()),
]

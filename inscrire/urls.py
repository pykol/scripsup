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

parametrage_urlpatterns = [
	path('import_structures',
		views.parametrage.ImportStructuresView.as_view(),
		name='parametrage_import_structures'),
	path('parcoursup/<int:pk>',
		views.parametrage.AccesParcoursupView.as_view(),
		name='parametrage_parcoursup_update'),
	path('parcoursup/synchronisation',
		views.parametrage.AccesParcoursupView.as_view(),
		name='parcoursup-synchro'),
]

rest_parcoursup_urlpatterns = [
	path('admissionCandidat', views.parcoursup.AdmissionView.as_view()),
	# Blague de Parcoursup qui ne respectait pas toujours la spec en 2019
	path('admissionCandidat/admissionCandidat', views.parcoursup.AdmissionView.as_view()),
]

auth_urlpatterns = [
	path('login/', views.auth.LoginView.as_view(), name='login'),
	path('bienvenue/', views.auth.EnvoiBienvenue.as_view(), name='envoi_bienvenue'),
	path('bienvenue/confirm/', views.auth.EnvoiBienvenueConfirm.as_view(), name='envoi_bienvenue_confirm'),
	path('', include('django.contrib.auth.urls')),
]

formation_urlpatterns = [
	path('',
		views.formation.FormationListView.as_view(),
		name='formation_list'),
	path('import_parcoursup',
		views.formation.ImportParcoursupView.as_view(),
		name='formation_import_parcoursup'),
	path('<slug:slug>',
		views.formation.FormationDetailView.as_view(),
		name='formation_detail'),
	path('<slug:slug>/update',
		views.formation.FormationUpdateView.as_view(),
		name='formation_update'),
]

autocomplete_urlpatterns = [
	path('pays',
		views.autocomplete.PaysAutocomplete.as_view(),
		name='autocomplete-pays'),
	path('commune',
		views.autocomplete.CommuneAutocomplete.as_view(),
		name='autocomplete-commune'),
	path('etablissement',
		views.autocomplete.EtablissementAutocomplete.as_view(),
		name='autocomplete-etablissement'),
]

urlpatterns = [
	path('', views.HomeView.as_view(), name='home'),
	path('accounts/', include(auth_urlpatterns)),
	path('parcoursup/', include(rest_parcoursup_urlpatterns)),
	path('parametrage/', include(parametrage_urlpatterns)),
	path('formation/', include(formation_urlpatterns)),
	path('candidat/<int:pk>/', views.candidats.CandidatDetail.as_view(), name='candidat_detail'),
	path('candidat/<int:pk>/dossier', views.candidats.CandidatDossier.as_view(),
		name='candidat_dossier'),
	path('candidat/<int:pk>/miseajour/', views.candidats.CandidatUpdate.as_view(),
		name='candidat_update'),
	path('responsablelegal/<int:pk>/', views.candidats.ResponsableLegal.as_view(),
		name='responsablelegal-detail'),
	path('fiche/<int:pk>/valider/',
		views.fiches.FicheValiderView.as_view(),
		name='fiche-valider'),
	path('fiche/<int:pk>/traiter/',
		views.fiches.FicheTraiterView.as_view(),
		name='fiche-traiter'),
	path('autocomplete/', include(autocomplete_urlpatterns)),
]

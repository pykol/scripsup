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

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.utils.translation import gettext, gettext_lazy as _

from inscrire.models import *

class InscrireUserCreationForm(UserCreationForm):
	class Meta:
		model = InscrireUser
		fields = ('email', 'role')

class InscrireUserAdmin(BaseUserAdmin):
	add_form = InscrireUserCreationForm
	add_fieldsets = ((None, {
			'classes': ('wide',),
			'fields': ('password1', 'password2', 'email', 'role'),
			}),)
	fieldsets = (
		(None, {'fields': ('password',)}),
		(_('Personal info'), {'fields': ('first_name', 'last_name',
			'email')}),
		(_('Permissions'), {'fields': ('role', 'is_active', 'is_staff', 'is_superuser',
									   'groups', 'user_permissions')}),
		(_('Important dates'), {'fields': ('last_login', 'date_joined')}),
		)

	ordering = ('email',)
	list_display = ('email', 'first_name', 'last_name', 'get_role_display', 'is_staff')
	search_fields = ('first_name', 'last_name', 'email')
admin.site.register(InscrireUser, InscrireUserAdmin)

class ResponsableLegalInline(admin.TabularInline):
	model = ResponsableLegal
	extra = 0

class CandidatActionLogInline(admin.TabularInline):
	model = CandidatActionLog
	extra = 0

@admin.register(Candidat)
class CandidatAdmin(admin.ModelAdmin):
	search_fields = ('dossier_parcoursup', 'first_name', 'last_name')
	list_display = ('last_name', 'first_name', 'dossier_parcoursup', 'voeu_actuel')
	autocomplete_fields = ('commune_naissance', 'pays_naissance',
		'nationalite',)
	inlines = (ResponsableLegalInline, CandidatActionLogInline)

@admin.register(ResponsableLegal)
class ResponsableLegalAdmin(admin.ModelAdmin):
	search_fields = ('last_name', 'first_name',)
	list_display = ('candidat', 'last_name', 'first_name',)

admin.site.register(CandidatActionLog)

@admin.register(Commune)
class CommuneAdmin(admin.ModelAdmin):
	list_display = ('nom_riche', 'code_insee')
	search_fields = ('nom_riche', 'code_insee')

@admin.register(Pays)
class PaysAdmin(admin.ModelAdmin):
	list_display = ('libelle', 'code_iso2')
	search_fields = ('libelle',)

admin.site.register(Profession)

@admin.register(Etablissement)
class EtablissementAdmin(admin.ModelAdmin):
	list_filter = ('inscriptions',)
	search_fields = ('nom', 'numero_uai')

	def get_form(self, *args, **kwargs):
		"""Met à jour la liste des champs "excluables" """
		ChampExclu.mise_a_jour()
		return super().get_form(*args, **kwargs)

@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
	list_display = ('nom', 'etablissement', 'email', 'code_parcoursup')
	list_filter = (('etablissement', admin.RelatedOnlyFieldListFilter),)
	autocomplete_fields = ('etablissement',)

admin.site.register(ParcoursupUser)
admin.site.register(ParcoursupMessageRecuLog)
admin.site.register(ParcoursupMessageEnvoyeLog)

class HistoriqueVoeuInline(admin.TabularInline):
	model = HistoriqueVoeu
	extra = 0

@admin.register(Voeu)
class VoeuAdmin(admin.ModelAdmin):
	list_display = ('candidat', 'formation', 'get_etat_display')
	inlines = (HistoriqueVoeuInline,)

@admin.register(FicheIdentite)
class FicheIdentiteAdmin(admin.ModelAdmin):
	search_fields = ('candidat',)
	list_display = ('candidat', 'get_etat_display')
	autocomplete_fields = ('commune_naissance', 'pays_naissance',
		'ville', 'pays', 'responsables',)

@admin.register(PieceJustificative)
class PieceJustificativeAdmin(admin.ModelAdmin):
	list_display = ('nom', 'etablissement', 'formation', 'modalite')

admin.site.register(FicheScolarite)
admin.site.register(FicheHebergement)
admin.site.register(FicheScolariteAnterieure)
admin.site.register(BulletinScolaire)
admin.site.register(FicheBourse)
admin.site.register(FicheReglement)
admin.site.register(FicheInternat)
admin.site.register(FicheCesure)
admin.site.register(FichePieceJustificative)
admin.site.register(ChampExclu)

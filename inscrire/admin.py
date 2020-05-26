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

admin.site.register(Candidat)
admin.site.register(ResponsableLegal)
admin.site.register(CandidatActionLog)
admin.site.register(Commune)
admin.site.register(Pays)
admin.site.register(Profession)
admin.site.register(Etablissement)
admin.site.register(Formation)
admin.site.register(ParcoursupUser)
admin.site.register(ParcoursupMessageRecuLog)
admin.site.register(ParcoursupMessageEnvoyeLog)
admin.site.register(Voeu)
admin.site.register(HistoriqueVoeu)
admin.site.register(FicheIdentite)
admin.site.register(FicheScolarite)
admin.site.register(FicheHebergement)
admin.site.register(FicheScolariteAnterieure)
admin.site.register(BulletinScolaire)
admin.site.register(FicheBourse)
admin.site.register(FicheReglement)
admin.site.register(FicheInternat)
admin.site.register(FicheCesure)

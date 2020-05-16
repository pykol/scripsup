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

from inscrire.models import *

admin.site.register(InscrireUser)
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

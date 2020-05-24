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

from dal import autocomplete

from inscrire.models import Pays, Commune, Etablissement

class PaysAutocomplete(autocomplete.Select2QuerySetView):
	def get_queryset(self):
		if not self.request.user.is_authenticated:
			return Pays.objects.none()

		qs = Pays.objects.all()

		if self.q:
			qs = qs.filter(libelle__icontains=self.q)

		return qs

class CommuneAutocomplete(autocomplete.Select2QuerySetView):
	def get_queryset(self):
		if not self.request.user.is_authenticated:
			return Commune.objects.none()

		qs = Commune.objects.all()

		if self.q:
			qs = qs.filter(libelle__icontains=self.q)

		return qs

class EtablissementAutocomplete(autocomplete.Select2QuerySetView):
	def get_queryset(self):
		if not self.request.user.is_authenticated:
			return Etablissement.objects.none()

		qs = Etablissement.objects.all()

		if self.q:
			qs = qs.filter(nom__icontains=self.q)

		return qs

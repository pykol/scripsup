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

"""
Vues permettant le paramétrage des formations gérées
"""
from django.views.generic import FormView, UpdateView

class ImportStructuresView(FormView):
	"""
	Import des formations depuis le fichier SIECLE Structures
	"""
	pass

class AccesParcoursupView(UpdateView):
	"""
	Paramétrage d'un accès à l'interface synchrone de Parcoursup
	"""
	pass
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

from django.contrib.auth.mixins import UserPassesTestMixin

from inscrire.models import InscrireUser

class AccessTechniqueMixin(UserPassesTestMixin):
	"""
	Mixin qui donne accès à des bouts techniques de l'interface
	"""
	def test_func(self):
		return self.request.user.is_staff or self.request.user.is_superuser

class AccessDirectionMixin(UserPassesTestMixin):
	"""
	Mixin qui filtre l'accès à une vue en le réservant à la direction.
	"""
	def test_func(self):
		return self.request.user.role == InscrireUser.ROLE_DIRECTION

class AccessGestionnaireMixin(UserPassesTestMixin):
	"""
	Mixin qui filtre l'accès à une vue en le réservant à des comptes de
	gestionnaires du lycée.
	"""
	def test_func(self):
		return self.request.user.est_gestionnaire()

class AccessPersonnelMixin(UserPassesTestMixin):
	"""
	Mixin qui filtre l'accès à une vue en le réservant à des comptes de
	personnels du lycée.
	"""
	def test_func(self):
		return self.request.user.est_gestionnaire() or \
				self.request.user.role == InscrireUser.ROLE_PROFESSEUR

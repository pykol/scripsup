# -*- coding:utf8 -*-

# pyKol - Gestion de colles en CPGE
# Copyright (c) 2018 Florian Hatat
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

from django.db import models
from django.contrib.auth.models import AbstractUser

class InscrireUser(AbstractUser):
    """
    Utilisateurs de ScripSup

    Il peut s'agir des personnels du lycée, des candidats qui veulent
    s'inscrire, ou de Parcoursup via son API.

    Au lieu d'utiliser un nom d'utilisateur, ce que fait Django par
    défaut, on identifie plutôt les utilisateurs par leur adresse
    e-mail.
    """
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    email = models.EmailField(
            verbose_name='adresse e-mail',
            max_length=255,
            unique=True,
    )
    username = None

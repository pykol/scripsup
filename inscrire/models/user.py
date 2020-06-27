# -*- coding:utf8 -*-

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

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
	"""Define a model manager for User model with no username field."""

	use_in_migrations = True

	def _create_user(self, email, password, **extra_fields):
		"""Create and save a User with the given email and password."""
		if not email:
			raise ValueError('The given email must be set')
		email = self.normalize_email(email)
		user = self.model(email=email, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_user(self, email, password=None, **extra_fields):
		"""Create and save a regular User with the given email and password."""
		extra_fields.setdefault('is_staff', False)
		extra_fields.setdefault('is_superuser', False)
		return self._create_user(email, password, **extra_fields)

	def create_superuser(self, email, password, **extra_fields):
		"""Create and save a SuperUser with the given email and password."""
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)

		if extra_fields.get('is_staff') is not True:
			raise ValueError('Superuser must have is_staff=True.')
		if extra_fields.get('is_superuser') is not True:
			raise ValueError('Superuser must have is_superuser=True.')

		return self._create_user(email, password, **extra_fields)

	# On redéfinit cette méthode, présente dans BaseUserManager, car
	# celle d'origine ne prend pas en compte l'option null=True sur le
	# champ email : elle renvoie '' au lieu de None.
	@classmethod
	def normalize_email(cls, email):
		"""
		Normalize the email address by lowercasing the domain part of it.
		"""
		email = email or ''
		try:
			email_name, domain_part = email.strip().rsplit('@', 1)
		except ValueError:
			pass
		else:
			email = email_name + '@' + domain_part.lower()
		return email or None

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
	REQUIRED_FIELDS = ['role',]
	objects = UserManager()

	email = models.EmailField(
			verbose_name='adresse e-mail',
			max_length=255,
			unique=True,
	)
	username = None

	ROLE_DIRECTION = 1
	ROLE_SECRETARIAT = 2
	ROLE_PROFESSEUR = 3
	ROLE_VIESCOLAIRE = 4
	ROLE_INTENDANCE = 5
	ROLE_ETUDIANT = 6
	ROLE_PARCOURSUP = 7
	ROLE_ADMINISTRATEUR = 8
	ROLE_CHOICES = (
			(ROLE_DIRECTION, "direction"),
			(ROLE_SECRETARIAT, "secrétariat"),
			(ROLE_PROFESSEUR, "professeur"),
			(ROLE_VIESCOLAIRE, "vie scolaire"),
			(ROLE_INTENDANCE, "intendance"),
			(ROLE_ETUDIANT, "étudiant"),
			(ROLE_PARCOURSUP, "Parcoursup"),
		)
	role = models.PositiveSmallIntegerField(verbose_name="rôle",
			choices=ROLE_CHOICES)

	def est_gestionnaire(self):
		return self.role in (InscrireUser.ROLE_DIRECTION,
				InscrireUser.ROLE_SECRETARIAT,
				InscrireUser.ROLE_VIESCOLAIRE,
				InscrireUser.ROLE_INTENDANCE,
				InscrireUser.ROLE_ADMINISTRATEUR)

	def est_administrateur(self):
		return self.role==InscrireUser.ROLE_ADMINISTRATEUR

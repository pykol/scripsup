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
from django.conf import settings

from .personnes import Candidat
from .formation import Etablissement, Formation

class ParcoursupUserManager(models.Manager):
    def authenticate(self, username, password):
        """
        Renvoie l'utilisateur désigné par le nom d'utilisateur et le mot
        de passe donnés en paramètre.

        Lève l'exception ParcoursupUser.DoesNotExist si l'utilisateur
        n'existe pas ou si le mot de passe n'est pas correct.
        """
        user = self.get(username=username)
        if not user.check_password(password):
            raise user.DoesNotExist

        return user

class ParcoursupUser(models.Model):
    """
    Identifiants utilisés pour recevoir et envoyer des messages via
    l'API Parcoursup
    """
    etablissement = models.ForeignKey(Etablissement,
            on_delete=models.CASCADE)

    # Identifiants qui permettent à Parcoursup de se connecter à notre
    # servie pour envoyer les admis.
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Identifiants que l'on doit utiliser pour envoyer des données à
    # Parcoursup. Le mot de passe est stocké en clair, c'est ainsi qu'on
    # doit l'envoyer à Parcoursup dans les requêtes.
    adresse_api = models.URLField(max_length=300)
    remontee_username = models.CharField(max_length=50)
    remontee_password = models.CharField(max_length=128)

    objects = ParcoursupUserManager()

    def check_password(self, raw_password):
        """
        Renvoie True lorsque le mot de passe en clair correspond à celui
        de l'utilisateur.
        """
        def setter(raw_password):
            self.password = make_password(raw_password)
            self.save(update_fields=["password"])

        if not check_password(raw_password, self.password, setter):
            # En cas d'échec, on ralentit le retour pour prendre à peu
            # près le même temps que si setter avait été appelé.
            make_password(raw_password)
            return False

        return True

class ParcoursupMessageRecuLog(models.Model):
    """
    Journal des messages reçus depuis Parcoursup
    """
    date = models.DateTimeField()
    ip_source = models.GenericIPAddressField()
    user = models.ForeignKey(ParcoursupUser, on_delete=models.SET_NULL,
            blank=True, null=True)
    endpoint = models.CharField(max_length=100)
    message = models.CharField(max_length=200)
    succes = models.BooleanField()
    payload = models.BinaryField(verbose_name="données reçues",
            blank=True, default=b'', null=True)

class ParcoursupMessageEnvoyeLog(models.Model):
    """
    Journal des messages envoyés à Parcoursup
    """
    date = models.DateTimeField()

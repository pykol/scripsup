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

from .user import InscrireUser
from .personnes import Personne, Candidat, ResponsableLegal, \
		CandidatActionLog, Commune, Pays, Profession
from .formation import Etablissement, Formation, MefMatiere, MefOption, \
		PieceJustificative, ChampExclu, Classement
from .parcoursup import ParcoursupUserManager, ParcoursupUser, \
		ParcoursupMessageRecuLog, ParcoursupMessageEnvoyeLog, \
		Voeu, HistoriqueVoeu, EtatVoeu
from .fiches import Fiche, FicheIdentite, FicheScolarite, \
		FicheHebergement, FicheScolariteAnterieure, BulletinScolaire, \
		FicheBourse, FicheReglement, FicheInternat, FicheCesure, \
		FichePieceJustificative, FichePieceJustificativeSuivi, EnteteFiche
from .mailing import Mailing, Envoi

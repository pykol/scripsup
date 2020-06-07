# -*- coding: utf-8 -*-

# Inscrisup - Gestion des inscriptions administratives après Parcoursup
# Copyright (c) 2019 Florian Hatat
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
Utilitaires pour lire les exports d'admis de Parcoursup
"""

import csv

from inscrire.models import Pays, Commune
from .parcoursup_rest import ParcoursupCandidat, ParcoursupProposition
from .utils import parse_french_date

def parse_export_standard(export_fh, code_etablissement, code_formation):
	"""
	Prend en paramètre un export Parcousup, soit standard soit
	paramétrable, et renvoie la liste des admissions contenues dans ce
	fichier.

	Chaque entrée de la liste a le même format que ce qui est produit
	par l'API REST (dictionnaire avec le candidat et les propositions).
	La liste des responsables légaux est vide, cette information n'est
	pas donnée dans les fichiers exportés par Parcoursup.

	Pour les fichiers paramétrables, il faut faire attention à inclure
	toutes les colonnes nécessaires.

	Ni l'établissement ni la formation ne sont présents dans l'export
	standard. Ils sont présents dans les exports paramétrables mais sous
	une forme textuelle non exploitable. Il faut donc les donner ici en
	paramètres pour remplir les données de la proposition.
	"""
	propositions = []
	for export_ligne in csv.DictReader(export_fh, delimiter=';'):
		candidat_defaults = {
				'nom': export_ligne['Nom'],
				'prenom': export_ligne['Prénom'],

				'email': export_ligne.get('e-mail du candidat',
					export_ligne.get('Adresse mail')),

				'date_naissance': parse_french_date(
					export_ligne.get('Date de Naissance',
					export_ligne.get('Date de naissance'))),

				'code': export_ligne.get('Numéro candidat',
					export_ligne.get('Numéro')),

				'ine': export_ligne.get('Numéro INE'),

				'telephone_fixe': export_ligne.get('Téléphone fixe',
					export_ligne.get('Téléphone')),

				'telephone_mobile': export_ligne.get('Téléphone mobile'),

				'sexe': ParcoursupCandidat.GENRE_HOMME
					if export_ligne.get('Etat civil',
						export_ligne['Civilité']) == 'M.'
					else ParcoursupCandidat.GENRE_FEMME,

				'nationalite': 'FR' if export_ligne.get('Nationalité') == 'FR' else None,

				#TODO à implémenter quand on aura les premiers résultats
				# de bac, pour l'instant j'ignore quel format va
				# choisir Parcoursup dans son fichier.
				'bac_date': None,
				'bac_serie': export_ligne.get('Série diplôme'),
				'bac_mention': export_ligne.get('Mention diplôme'),
		}
		try:
			candidat_defaults['pays_naissance'] = Pays.objects.get(
					nom__iexact=export_ligne.get('Pays de naissance')).pk
		except:
			pass

		try:
			candidat_defaults['commune_naissance'] = Commune.objets.get(
					nom__iexact=export_ligne.get('Ville de naissance')).pk
		except:
			pass

		candidat_defaults['adresse'] = ParcoursupCandidat.formate_adresse(
				libellePaysadresse=export_ligne.get('Pays') or 'France',
				libellecommune=export_ligne['Commune'],
				adresse1=export_ligne['Adresse 1'],
				adresse2=export_ligne['Adresse 2'],
				adresse3=export_ligne['Adresse 3'],
				codepostal=export_ligne['Code postal'],
			)

		candidat = ParcoursupCandidat(**candidat_defaults)
		proposition = ParcoursupProposition(
				code_formation=code_formation,
				code_etablissement=code_etablissement,
				cesure=export_ligne.get('Année de césure', 'non').lower() == 'oui',
				internat=
					export_ligne.get('Internat', 'non').lower() == 'oui' or
					export_ligne.get('Internat obtenu', 'Sans internat').lower() == 'avec internat',
				date=datetime.strptime(export_ligne.get('date réponse',
					export_ligne.get('Date réponse')), '%d/%m/%Y %H:%M'),
				#TODO info présente dans l'export standard, exploitable ?
				etat=ParcoursupProposition.ETAT_ACCEPTEE,
		)
		propositions.append({
			'candidat': candidat,
			'proposition': proposition,
			'responsables': [],
		})
	return propositions

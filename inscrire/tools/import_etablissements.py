#! env python3
# -*- coding: utf-8 -*-

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
Import de la liste des établissements depuis un fichier CSV

https://www.data.gouv.fr/fr/datasets/adresse-et-geolocalisation-des-etablissements-denseignement-du-premier-et-second-degres-1/
"""

import sys
import csv
import json
import re

def norm(chaine):
	return re.sub('\n+', '\n', chaine.strip())

def main():
	etablissements = []

	with open(sys.argv[1], 'r') as etab_file:
		etab_csv = csv.DictReader(etab_file, delimiter=';')

		for idx, ligne in enumerate(etab_csv):
			nature_uai = int(ligne['Code nature'])

			# On importe uniquement les lycées généraux
			if nature_uai < 300 or nature_uai >= 310:
				continue

			denomination = norm("{denomination_principale} {patronyme}".format(
				denomination_principale=ligne['Dénomination principale'],
				patronyme=ligne['Patronyme uai']))

			appellation = norm(ligne['Appellation officielle']) or denomination

			etablissements.append({
				'model': 'inscrire.etablissement',
				'pk': ligne['Code établissement'],
				'fields': {
					'nom': appellation,
				}
			})

	print(json.dumps(etablissements, indent=4))

main()

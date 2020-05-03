#!env python3
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
Outil qui génère les données initiales des pays au format JSON pour
Django, depuis le fichier des pays CSV publié par l'INSEE.

URL INSEE pour 2020 : https://www.insee.fr/fr/information/4316069
"""

import sys
from collections import namedtuple
import zipfile
import json
import csv
import io

Pays = namedtuple('Pays',
		('code_iso2', 'code_iso3', 'code_isonum', 'libelle_cog', 'libelle_jo',))

def pays_list(filename):
	pays = []

	try:
		pays_zip = zipfile.ZipFile(filename)
		pays_csv = io.TextIOWrapper(pays_zip.open(pays_zip.namelist()[0]), 'utf-8')
	except zipfile.BadZipFile:
		pays_csv = open(filename, newline='')

	for ligne in csv.DictReader(pays_csv):
		pays.append(Pays(
			code_iso2=ligne['codeiso2'],
			code_iso3=ligne['codeiso3'],
			code_isonum=ligne['codenum3'],
			libelle_cog=ligne['libcog'],
			libelle_jo=ligne['libenr'],
		))

	return pays

def to_django_json(pays_list):
	json = []
	for pays in pays_list:
		json.append({
			'model': 'inscrire.Pays',
			'pk': pays.code_iso2,
			'fields': {
				'code_iso3': pays.code_iso3,
				'num_iso': pays.code_isonum,
				'libelle': pays.libelle_cog,
				}
			})
	return json

def main():
	return print(
			json.dumps(to_django_json(pays_list(sys.argv[1])),
				indent=4
		))

if __name__ == '__main__':
	main()

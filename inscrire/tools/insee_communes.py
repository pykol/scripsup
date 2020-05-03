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
Outil qui génère les données initiales des communes au format JSON pour
Django, depuis le fichier des communes CSV publié par l'INSEE.

URL INSEE pour 2020 : https://www.insee.fr/fr/information/4316069
"""

import sys
from collections import namedtuple
import zipfile
import json
import csv
import io

Commune = namedtuple('Commune',
		('code', 'ncc', 'nenr', 'libelle'))

def commune_list(filename):
	communes = []

	try:
		commune_zip = zipfile.ZipFile(filename)
		commune_csv = io.TextIOWrapper(commune_zip.open(commune_zip.namelist()[0]), 'utf-8')
	except zipfile.BadZipFile:
		commune_csv = open(filename, newline='')

	for ligne in csv.DictReader(commune_csv):
		communes.append(Commune(
			code=ligne['com'],
			ncc=ligne['ncc'],
			nenr=ligne['nccenr'],
			libelle=ligne['libelle'],
		))

	return communes

def to_django_json(commune_list):
	json = []
	for commune in commune_list:
		json.append({
			'model': 'inscrire.Commune',
			'pk': commune.code,
			'fields': {
				'nom_clair': commune.ncc,
				'nom_riche': commune.nenr,
				'libelle': commune.libelle,
				}
			})
	return json

def main():
	return print(
			json.dumps(to_django_json(commune_list(sys.argv[1])),
				indent=4
		))

if __name__ == '__main__':
	main()

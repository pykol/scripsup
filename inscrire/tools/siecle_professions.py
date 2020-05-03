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
Outil qui génère le dictionnaire des professions à partir d'un fichier
Nomenclature exporté depuis SIECLE.
"""

import sys
from collections import namedtuple
import xml.etree.ElementTree as ElementTree
import zipfile
import json

Profession = namedtuple('Profession',
		('code', 'libelle_long', 'libelle_court',))

def profession_dict(filename):
	professions = {}

	# Pour ne pas se prendre la tête, on accepte les exports SIECLE
	# qu'ils soient zippés ou non
	try:
		nomenclature_zip = zipfile.ZipFile(filename)
		nomenclature_file = nomenclature_zip.open(nomenclature_zip.namelist()[0])
	except zipfile.BadZipFile:
		nomenclature_file = open(filename)
	nomenclature_et = ElementTree.parse(nomenclature_file)

	professions_et = nomenclature_et.getroot().find('./DONNEES/PROFESSIONS')
	for profession in professions_et.findall('PROFESSION'):
		code = int(profession.attrib['CODE_PROFESSION'])
		professions[code] = Profession(
				code=code,
				libelle_long=profession.find('LIBELLE_LONG_PCS').text,
				libelle_court=profession.find('LIBELLE_COURT_PCS').text,
			)
	return professions

def to_django_json(professions):
	json = []
	for profession in professions.values():
		json.append({
			'model': 'inscrire.Profession',
			'pk': profession.code,
			'fields': {
				'libelle_court': profession.libelle_court,
				'libelle_long': profession.libelle_long,
				}
			})
	return json

def main():
	return print(
			json.dumps(to_django_json(profession_dict(sys.argv[1])),
				indent=4
		))

if __name__ == '__main__':
	main()

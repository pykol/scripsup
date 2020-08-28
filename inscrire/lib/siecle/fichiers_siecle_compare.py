# Pour comparaison avec les données élèves de SIECLE
# Fonctionnalité très grosièrement développée

from datetime import datetime
import xml.etree.ElementTree as ElementTree

from .interfaces import MEF, Matiere, MEFProgramme, MEFOption
from .fichiers import ExportSiecle


class ElevesSansAdresses(ExportSiecle):
	def eleves(self):
		lexique_eleves={
			'ine':'ID_NATIONAL',
			'email':'MEL',
			'nom': 'NOM_DE_FAMILLE',
			'prenom':'PRENOM',
			'genre':'CODE_SEXE',
			'mobile':'TEL_PORTABLE',
		}
		lexique_options={
			'numero': 'NUM_OPTION',
			'modalite': 'CODE_MODALITE_ELECT',
			'code_matiere': 'CODE_MATIERE'
		}
		dic_eleves={}
		for eleve in self.xml.getroot().findall('./DONNEES/ELEVES/'):
			dic={}
			dic_eleves.update({eleve.get('ELEVE_ID'):dic})
			for key, code in lexique_eleves.items():
				valeur=eleve.find(code)
				dic[key]=valeur.text if valeur!=None else ""
			dic['options']=[]
			dic['structure']=""
			dic["bourse"]=""
		for options in self.xml.getroot().findall('.DONNEES/OPTIONS/'):
			L=dic_eleves[options.get('ELEVE_ID')]['options']
			for option in options.findall('OPTIONS_ELEVE'):
				dic={}
				L.append(dic)
				for key, code in lexique_options.items():
					valeur=option.find(code)
					dic[key]=valeur.text if valeur!=None else ""
		for structure_eleve in self.xml.getroot().findall('.DONNEES/STRUCTURES/'):
			dic_eleves[structure_eleve.get('ELEVE_ID')]['structure']=structure_eleve.find('STRUCTURE/CODE_STRUCTURE').text
		for bourse in self.xml.getroot().findall('.DONNEES/BOURSES/'):
			dic_eleves[bourse.get('ELEVE_ID')]['bourse']=bourse.find('CODE_BOURSE').text
		return dic_eleves

class Structures(ExportSiecle):
	def structures(self):
		"""retourne un dictionnaire dont les clés sont
		les codes mefs et les valeurs sont des sets contentant
		les divisions correspondantes"""
		dic_structures={}
		for division in self.xml.getroot().findall('.DONNEES/DIVISIONS/'):
			for mef in division.findall('MEFS_APPARTENANCE/MEF_APPARTENANCE'):
				code_mef=mef.find('CODE_MEF').text
				if not code_mef in dic_structures:
					dic_structures[code_mef]=set()
				dic_structures[code_mef].add(division.get('CODE_STRUCTURE'))
		return dic_structures

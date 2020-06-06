from datetime import datetime
import xml.etree.ElementTree as ElementTree

from .interfaces import MEF, Matiere, MEFProgramme, MEFOption

class ExportSiecle:
	def __init__(self, fh):
		self.file_handle = fh
		self.xml = ElementTree.parse(fh)

	def parametres(self):
		params = self.xml.getroot().find('./PARAMETRES')
		return {
			'uai': params.find('UAJ').text,
			'annee_scolaire': params.find('ANNEE_SCOLAIRE').text,
			'date_export': datetime.strptime(
				params.find('DATE_EXPORT').text,
				'%d/%m/%Y').date(),
			'horodatage': datetime.strptime(
				params.find('HORODATAGE').text,
				'%d/%m/%Y %H:%M:%S')
		}

	@classmethod
	def guess_type(xml_et):
		return {
			'BEE_NOMENCLATURES': Nomenclature,
			'BEE_STRUCTURES': Structures,
		}.get(xml_et.getroot().tag)

class Nomenclature(ExportSiecle):
	def mefs(self):
		mefs = {}
		for mef_et in self.xml.getroot().findall('./DONNEES/MEFS/MEF'):
			code_mef = mef_et.attrib['CODE_MEF']
			try:
				nb_opt_oblig = int(mef_et.find('NB_OPT_OBLIG').text)
			except:
				nb_opt_oblig = None
			try:
				nb_opt_mini = int(mef_et.find('NB_OPT_MINI').text)
			except:
				nb_opt_mini = None

			mefs[code_mef] = MEF(
				code=mef_et.attrib['CODE_MEF'],
				formation=mef_et.find('FORMATION').text,
				libelle_long=mef_et.find('LIBELLE_LONG').text,
				nb_opt_oblig=nb_opt_oblig,
				nb_opt_mini=nb_opt_mini,
			)
		matieres = self.matieres()

		for programme_et in self.xml.getroot().findall('./DONNEES/PROGRAMMES/PROGRAMME'):
			code_mef = programme_et.find('CODE_MEF').text
			mefs[code_mef].programme.append(
					MEFProgramme(mef=mefs[code_mef],
						matiere=matieres[programme_et.find('CODE_MATIERE').text],
						modalite_election=programme_et.find('CODE_MODALITE_ELECT').text,
						horaire=programme_et.find('HORAIRE').text,
					)
				)

		for option_et in self.xml.getroot().findall('./DONNEES/OPTIONS_OBLIGATOIRES/OPTION_OBLIGATOIRE'):
			code_mef = option_et.find('CODE_MEF').text
			option = MEFOption(mef=mefs[code_mef],
				matiere=matieres[option_et.find('CODE_MATIERE').text],
				rang=int(option_et.find('RANG_OPTION').text))
			mefs[code_mef].options_obligatoires.append(option)

		return mefs

	def matieres(self):
		matieres = {}
		for matiere_et in self.xml.getroot().findall('./DONNEES/MATIERES/MATIERE'):
			code_matiere = matiere_et.attrib['CODE_MATIERE']
			matieres[code_matiere] = Matiere(
					code=code_matiere,
					code_gestion=matiere_et.find('CODE_GESTION').text,
					libelle_court=matiere_et.find('LIBELLE_COURT').text,
					libelle_long=matiere_et.find('LIBELLE_LONG').text,
					libelle_edition=matiere_et.find('LIBELLE_EDITION').text,
					matiere_etp=matiere_et.find('MATIERE_ETP').text,
				)
		return matieres

class Structures(ExportSiecle):
	def mefs(self):
		"""
		Renvoie l'ensemble es codes MEF pour lesquels il existe une
		division avec ce code.
		"""
		codes_mefs = set()
		for mef_et in self.xml.getroot().findall('./DONNEES/DIVISIONS/DIVISION/MEFS_APPARTENANCE/MEF_APPARTENANCE/CODE_MEF'):
			codes_mefs.add(mef_et.text)
		return codes_mefs

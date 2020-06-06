class MEF:
	"""
	Module élémentaire de formation
	"""
	def __init__(self, **kwargs):
		self.code = kwargs['code']
		self.formation = kwargs.get('formation', "")
		self.specialite = kwargs.get('specialite', "")
		self.libelle_long = kwargs.get('libelle_long', "")
		self.statut = kwargs.get('statut', "")
		self.code_mefstat = kwargs.get('code_mefstat', "")
		self.nb_opt_oblig = kwargs.get('nb_opt_oblig', 0)
		self.nb_opt_mini = kwargs.get('nb_opt_mini', 0)
		self.renforcement_langues = kwargs.get('renforcement_langues', 0)
		self.inscription_etab = kwargs.get('inscription_etab', 0)
		self.mef_origine = kwargs.get('mef_origine', 1)
		self.mef_selectionne = kwargs.get('mef_selectionne', 0)
		self.selorig = kwargs.get('selorig', 1)
		self.date_ouverture = kwargs.get('date_ouverture', None)
		self.date_fermeture = kwargs.get('date_fermeture', None)
		self.programme = kwargs.get('programme', [])
		self.options_obligatoires = kwargs.get('options_obligatoires', [])

class Matiere:
	"""
	Matière
	"""
	def __init__(self, **kwargs):
		self.code = kwargs['code']
		self.code_gestion = kwargs.get('code_gestion')
		self.libelle_court = kwargs.get('libelle_court')
		self.libelle_long = kwargs.get('libelle_long')
		self.libelle_edition = kwargs.get('libelle_edition')
		self.matiere_etp = kwargs.get('matiere_etp')

	def __str__(self):
		return "{} - {}".format(self.code, self.libelle_long)

class MEFProgramme:
	def __init__(self, **kwargs):
		self.mef = kwargs['mef']
		self.matiere = kwargs['matiere']
		self.modalite_election = kwargs['modalite_election']
		self.horaire = kwargs.get('horaire')

class MEFOption:
	def __init__(self, **kwargs):
		self.mef = kwargs['mef']
		self.matiere = kwargs['matiere']
		self.rang = kwargs['rang']

	def __repr__(self):
		return "Option {} (rang {})".format(self.matiere.libelle_long, self.rang)

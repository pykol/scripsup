# -*- coding:utf8 -*-

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
Informations d'inscription des candidats dans une formation.

Les informations sont regroupées par fiches. Chaque fiche regroupe les
informations spécifiques à un service donné.
"""

from django.db import models
from django.db.models import Q
from polymorphic.models import PolymorphicModel, PolymorphicManager
import localflavor.generic.models as lfmodels

from .personnes import Candidat, Commune, Pays, ResponsableLegal
from .formation import MefOption, Formation, Etablissement

class FicheManager(PolymorphicManager):
	"""
	Manager qui permet la création rapide de toutes les fiches pour un
	candidat.
	"""
	def create_applicable(self, voeu, **kwargs):
		"""
		Méthode qui crée toutes les classes héritées de Fiche, parmi
		celles listées dans all_fiche (défini ci-dessous), qui sont
		applicables au voeu donné (vérifié avec la méthode de classe
		applicable).
		"""
		fiches = []
		all_fiche = SelectFiches.get(voeu.formation.etablissement).all_fiche()
		parcoursup = kwargs.pop('parcoursup', {})
		for fiche_kls in filter(lambda kls: kls.applicable(voeu),
				all_fiche):
			fiche = fiche_kls(candidat=voeu.candidat, **kwargs)
			if parcoursup:
				fiche.update_from_parcoursup(parcoursup)
			fiche.save()
			fiches.append(fiche)
		return fiches

	def create_or_update_applicable(self, voeu, **kwargs):
		"""
		Méthode qui crée les fiches, selon les mêmes critères que
		create_applicable, mais qui tente de recycler d'anciennes fiches
		qui existaient éventuellement auparavant.

		Ceci permet à un candidat de retrouver des données qu'il aurait
		saisies précédemment en cas de modification reçue depuis
		Parcoursup. Parcoursup n'envoie normalement que les candidats
		admis à titre définitif mais des changements peuvent malgré
		tout avoir lieu, par exemple lorsqu'un candidat démissionne par
		erreur (et le lycée d'accueil rétablit son vœu), ou bien si un
		candidat disparait puis revient suite à des vœux en procédure
		complémentaire.

		Renvoie une liste de couples (fiche, created) formés chacun
		d'une instance d'une classe héritée de Fiche et d'un booléen qui
		vaut True quand la fiche est nouvelle et False quand elle a
		juste été mise à jour.
		"""
		fiches = []
		all_fiche = SelectFiches.get(voeu.formation.etablissement).all_fiche()
		parcoursup = kwargs.pop('parcoursup', {})

		fiches_applicables = dict([(kls, None)
			for kls in filter(lambda kls: kls.applicable(voeu), all_fiche)])

		# On commence par recycler les fiches existantes
		for fiche in Fiche.objects.filter(candidat=voeu.candidat):
			if type(fiche) in fiches_applicables:
				if fiche.recyclable(voeu):
					fiches_applicables[type(fiche)] = fiche

					# On remet la fiche en mode édition
					if fiche.etat in (Fiche.ETAT_CONFIRMEE,
							Fiche.ETAT_ANNULEE):
						fiche.etat = Fiche.ETAT_EDITION
						fiche.save()

					fiches.append((fiche, False))
				else:
					# L'ancienne fiche ne peut pas servir, on en créera
					# une nouvelle à la fin de la fonction. Pour
					# l'instant, on marque l'actuelle comme étant
					# annulée.
					fiche.etat = Fiche.ETAT_ANNULEE
					fiche.save()
			else:
				# Il existe une fiche qui n'est pas applicable, on
				# l'annule.
				fiche.etat = Fiche.ETAT_ANNULEE
				fiche.save()

		# On crée enfin les instances manquantes
		for fiche_kls in fiches_applicables:
			if fiches_applicables[fiche_kls] is None:
				fiche = fiche_kls(candidat=voeu.candidat, **kwargs)
				fiche.save()
				fiches.append((fiche, True))

		# Enfin, on met à jour les données depuis Parcoursup si
		# nécessaire.
		if parcoursup:
			for (fiche, _) in fiches:
				fiche.update_from_parcoursup(parcoursup)

		return fiches


class Fiche(PolymorphicModel):
	"""
	Classe de base pour une fiche d'inscription.

	Grâce à django-polymorphic, les requêtes sur ce modèle renvoient
	directement des instances des bonnes sous-classes, ce qui permet de
	surcharger naturellement les méthodes.

	Le champ FICHE_LABEL est un libellé utilisable sur l'interface
	utilisateur.
	"""
	FICHE_LABEL = "Données d'inscription"
	valide = models.BooleanField(default=False)
	candidat = models.ForeignKey(Candidat, on_delete=models.CASCADE)

	ETAT_EDITION = 1
	ETAT_CONFIRMEE = 2
	ETAT_TERMINEE = 3
	ETAT_ANNULEE = 4
	ETAT_CHOICES = (
		(ETAT_EDITION, "fiche à compléter"),
		(ETAT_CONFIRMEE, "fiche confirmée"),
		(ETAT_TERMINEE, "validée par le gestionnaire"),
		(ETAT_ANNULEE, "annulée")
	)
	etat = models.PositiveSmallIntegerField(verbose_name="état",
			choices=ETAT_CHOICES, default=ETAT_EDITION)

	objects = FicheManager()

	@classmethod
	def applicable(kls, voeu):
		"""
		Méthode qui indique si une fiche est applicable à un vœu donné.

		Cette méthode renvoie un booléen si cette fiche est demandée
		pour l'inscription d'un candidat étant donné le vœu qu'il a
		accepté. L'implémentation de base renvoie toujours True. Cette
		méthode devrait être surchargée.
		"""
		return True

	def recyclable(self, voeu):
		"""
		Méthode qui indique si une fiche peut être réutilisée pour le
		nouveau vœu passé en paramètre, alors qu'elle avait été créée
		potentiellement à partir d'un autre vœu.
		"""
		return True

	def valider(self):
		"""
		Méthode qui indique si les données de la fiche sont complètes et
		valides. Dans ce cas, cette méthode change la valeur du champ
		valide de la fiche. Cette méthode doit être surchargée par les
		classes héritées, la méthode de base ne fait rien.
		"""
		pass

	def get_etat_class(self):
		"""
		Renvoie un nom de classe HTML représentant l'état de la fiche.
		"""
		return {
				Fiche.ETAT_EDITION: 'etat-edition',
				Fiche.ETAT_CONFIRMEE: 'etat-confirmee',
				Fiche.ETAT_TERMINEE: 'etat-terminee',
				Fiche.ETAT_ANNULEE: 'etat-annulee',
			}.get(self.etat, '')

	def update_from_parcoursup(self, parcoursup):
		"""
		Mise à jour des champs à partir des données Parcoursup
		"""
		pass

class FicheIdentite(Fiche):
	"""
	Informations concernant l'identité du candidat
	"""
	FICHE_LABEL = "Identité"

	def _photo_upload_to(instance, filename):
		return "photo/{psup}/{filename}".format(
				psup=instance.candidat.dossier_parcoursup,
				filename=filename)
	photo = models.ImageField(upload_to=_photo_upload_to,
			blank=True, null=True)

	def _piece_identite_upload_to(instance, filename):
		return "piece_identite/{psup}/{filename}".format(
				psup=instance.candidat.dossier_parcoursup,
				filename=filename)
	piece_identite = models.FileField(upload_to=_piece_identite_upload_to,
			blank=True, null=True)
	commune_naissance = models.ForeignKey(Commune,
			on_delete=models.PROTECT,
			blank=True, null=True, related_name='ficheidentite_naissance')
	commune_naissance_etranger = models.CharField(max_length=200,
			blank=True, null=False, default="")
	pays_naissance = models.ForeignKey(Pays, on_delete=models.PROTECT,
			blank=True, null=True,
			related_name='ficheidentite_naissance')
	responsables = models.ManyToManyField(ResponsableLegal)

	# Adresse, possiblement différente de celle renseignée par
	# Parcoursup dans le modèle Candidat.
	adresse = models.TextField(blank=True, default="")
	ville = models.ForeignKey(Commune, on_delete=models.PROTECT,
			blank=True, null=True,
			related_name='ficheidentite_residence')
	pays = models.ForeignKey(Pays, on_delete=models.PROTECT, blank=True,
			null=True, related_name='ficheidentite_residence')
	telephone = models.CharField(max_length=20,
			verbose_name="Téléphone personnel", blank=True, default="")

	class Meta:
		verbose_name = "fiche identité"
		verbose_name_plural = "fiches identité"

	def valider(self):
		self.valide = (
			(self.photo is not None) and
			(self.piece_identite is not None) and
			(self.commune_naissance is not None or
				bool(self.commune_naissance_etranger)) and
			(self.pays_naissance is not None)
		)

	def update_from_parcoursup(self, parcoursup):
		try:
			self.ville = Commune.objects.get(
					code_insee=parcoursup['candidat'].code_commune)
		except:
			pass

		try:
			# L'API Parcoursup dit que c'est le code ISO2 qui est
			# renvoyé. Sauf qu'en pratique, c'est le numéro INSEE... On
			# prend des précautions au cas où l'API change
			# silencieusement un jour pour coller à la documentation.
			self.pays = Pays.objects.get(
					Q(code_iso2=parcoursup['candidat'].code_pays)
					| Q(num_insee=parcoursup['candidat'].code_pays))
		except:
			pass

		try:
			self.commune_naissance = Commune.objects.get(
					code_insee=parcoursup['candidat'].commune_naissance)
		except:
			pass

		try:
			# L'API Parcoursup dit que c'est le code ISO2 qui est
			# renvoyé. Sauf qu'en pratique, c'est le numéro. On prend
			# des précautions au cas où l'API change silencieusement un
			# jour pour coller à la documentation.
			self.pays_naissance = Pays.objects.get(
					Q(code_iso2=parcoursup['candidat'].pays_naissance)
					| Q(num_insee=parcoursup['candidat'].pays_naissance))
		except:
			pass

		try:
			self.adresse = parcoursup['candidat'].adresse
		except:
			pass

		try:
			self.telephone = parcoursup['candidat'].telephone_mobile
		except:
			pass

		if not self.responsables.all():
			self.responsables.set(self.candidat.responsables.all())

		self.save()

class FicheScolariteAnterieure(Fiche):
	"""
	Scolarité antérieure
	"""
	FICHE_LABEL = "Scolarité antérieure"
	etablissement = models.ForeignKey(Etablissement,
			on_delete=models.PROTECT,
			blank=True, null=True)
	classe_terminale = models.CharField(max_length=20,
			verbose_name="classe de terminale suivie",
			blank=True, null=False, default="")
	specialite_terminale = models.CharField(max_length=100,
			verbose_name="spécialité en terminale",
			blank=True, null=False, default="")
	autre_formation = models.CharField(max_length=200,
			verbose_name="autre formation",
			blank=True, null=False, default="")

	class Meta:
		verbose_name = "fiche scolarité antérieure"
		verbose_name_plural = "fiches scolarité antérieure"

	def valider(self):
		self.valide = (
				(
					(self.etablissement is not None) or
					bool(self.autre_formation)
				)
				and bool(self.classe_terminale)
				and bool(self.specialite_terminale)
				and bool(self.bulletinscolaire_set.all())
			)

	def update_from_parcoursup(self, parcoursup):
		try:
			self.etablissement = Etablissement.objects.get(
					numero_uai=parcoursup['candidat'].etablissement_origine_uai)
		except:
			pass

		if self.etablissement is None and parcoursup['candidat'].etablissement_origine_nom:
			self.autre_formation = parcoursup['candidat'].etablissement_origine_nom

		self.specialite_terminale = parcoursup['candidat'].bac_serie or ''

		self.save()

class BulletinScolaire(models.Model):
	"""
	Copie d'un bulletin scolaire
	"""
	fiche_scolarite = models.ForeignKey(FicheScolariteAnterieure,
			on_delete=models.CASCADE)

	CLASSE_PREMIERE = 1
	CLASSE_TERMINALE = 2
	CLASSE_CHOICES = (
			(CLASSE_PREMIERE, "bulletin de première"),
			(CLASSE_TERMINALE, "bulletin de terminale"),
		)
	classe = models.PositiveSmallIntegerField(choices=CLASSE_CHOICES)

	def _bulletin_upload_to(instance, filename):
		return "bulletin/{psup}/{filename}".format(
				psup=instance.fiche_scolarite.candidat.dossier_parcoursup,
				filename=filename)
	bulletin = models.FileField(upload_to=_bulletin_upload_to)

	class Meta:
		verbose_name = "bulletin scolaire"
		verbose_name_plural = "bulletins scolaires"

class FicheBourse(Fiche):
	"""
	Bourse du supérieur
	"""
	FICHE_LABEL = "Bourse du supérieur"
	boursier = models.BooleanField(default=False)
	echelon = models.PositiveSmallIntegerField(verbose_name="échelon",
			blank=True, null=True)
	enfants_charge = models.PositiveSmallIntegerField(
			verbose_name="nombre d'enfants à charge (y compris l'étudiant)",
			default=1)
	enfants_secondaire = models.PositiveSmallIntegerField(
			verbose_name="nombre d'enfants en lycée ou en collège",
			default=0)
	enfants_etablissement = models.PositiveSmallIntegerField(
			verbose_name="nombre d'enfants dans l'établissement",
			default=1)

	def _attribution_bourse_upload_to(instance, filename):
		return "bourse_acb/{psup}/{filename}".format(
				psup=instance.candidat.dossier_parcoursup,
				filename=filename)
	attribution_bourse = models.FileField(
			verbose_name="copie de l'attestation conditionnelle de bourse",
			upload_to=_attribution_bourse_upload_to,
			blank=True, null=True)

	class Meta:
		verbose_name = "fiche bourse"
		verbose_name_plural = "fiches bourse"

	def valider(self):
		if self.boursier:
			self.valide = self.echelon is not None and \
					self.attribution_bourse is not None
		else:
			self.valide = True

class FicheReglement(Fiche):
	"""
	Règlement intérieur
	"""
	FICHE_LABEL = "Règlement intérieur"
	signature_reglement = models.DateTimeField(
			verbose_name="signature du règlement intérieur",
			blank=True, null=True)
	autorisation_parents_eleves = models.BooleanField(default=False)

	class Meta:
		verbose_name = "fiche règlement intérieur"
		verbose_name_plural = "fiches règlement intérieur"

	def valider(self):
		self.valide = self.signature_reglement is not None

class FicheScolarite(Fiche):
	"""
	Choix des options dans la formation
	"""
	FICHE_LABEL = "Choix des options"
	formation = models.ForeignKey(Formation, on_delete=models.CASCADE)
	options = models.ManyToManyField(MefOption)

	def recyclable(self, voeu):
		return voeu.formation == self.formation

	def save(self, *args, **kwargs):
		self.formation = self.candidat.voeu_actuel.formation
		super().save(*args, **kwargs)

	def valider(self):
		# On vérifie que toutes les options obligatoires ont été
		# choisies.
		rangs_disponibles = set(self.formation.mefoption_set.filter(
			modalite=MefOption.MODALITE_OBLIGATOIRE,
			inscriptions=True).values_list('rang',
					flat=True))
		rangs_choisis = set()
		for option in self.options.filter(modalite=MefOption.MODALITE_OBLIGATOIRE):
			# Cas de deux options exclusives pour le même rang
			if option.rang in rangs_choisis:
				self.valide = False
				break
			rangs_choisis.add(option.rang)
		else:
			self.valide = rangs_disponibles == rangs_choisis

	class Meta:
		verbose_name = "fiche scolarité"
		verbose_name_plural = "fiches scolarité"

class FicheHebergement(Fiche):
	"""
	Choix du mode d'hébergement
	"""
	FICHE_LABEL = "Mode d'hébergement"

	REGIME_EXTERNE = 0
	REGIME_DEMIPENSIONNAIRE = 1
	REGIME_INTERNEEXTERNE = 2
	REGIME_INTERNE = 3
	REGIME_CHOICES = (
		(REGIME_EXTERNE, "externe"),
		(REGIME_DEMIPENSIONNAIRE, "demi-pensionnaire"),
		(REGIME_INTERNEEXTERNE, "interne externé"),
		(REGIME_INTERNE, "interne"),
	)
	regime = models.PositiveSmallIntegerField(verbose_name="régime",
			choices=REGIME_CHOICES,
			blank=True, null=True)
	iban = lfmodels.IBANField(include_countries=('FR',),
			blank=True, null=True)
	bic = lfmodels.BICField(blank=True, null=True)
	titulaire_compte = models.CharField(max_length=200, blank=True,
			null=False, default="")

	class Meta:
		verbose_name = "fiche hébergement"
		verbose_name_plural = "fiches hébergement"

	def valider(self):
		self.valide = self.regime is not None

	def update_from_parcoursup(self, parcoursup):
		if parcoursup['proposition'].internat:
			self.regime = self.REGIME_INTERNE
		self.save()

class FicheInternat(Fiche):
	"""
	Renseignements spécifiques à l'internat
	"""
	FICHE_LABEL = "Internat"

	message = models.TextField(verbose_name="demandes particulières",
			default="", blank=True, null=False)

	@classmethod
	def applicable(kls, voeu):
		return voeu.internat

	class Meta:
		verbose_name = "fiche internat"
		verbose_name_plural = "fiches internat"

class FicheCesure(Fiche):
	"""
	Données à remplir en cas de demande de césure
	"""
	FICHE_LABEL = "Demande de césure"

	@classmethod
	def applicable(kls, voeu):
		return voeu.cesure

	class Meta:
		verbose_name = "fiche césure"
		verbose_name_plural = "fiches césure"

# Liste de toutes les fiches à essayer lors de la création d'un dossier.
# L'ordre dans cette liste détermine l'ordre d'affichage pour le
# candidat.
all_fiche = [
		FicheIdentite,
		FicheScolariteAnterieure,
		FicheScolarite,
		FicheHebergement,
		FicheInternat,
		FicheCesure,
		FicheBourse,
		FicheReglement,
	]


class SelectFiches(models.Model):
	"""Fiches sélectionnées par un établissement"""
	etablissement = models.OneToOneField(Etablissement, on_delete = models.CASCADE)

	ficheidentite = models.BooleanField(default = True, blank = True)
	fichescolariteanterieure = models.BooleanField(default = True, blank = True)
	fichescolarite = models.BooleanField(default = True, blank = True)
	fichehebergement = models.BooleanField(default = True, blank = True)
	ficheinternat =models.BooleanField(default = True, blank = True)
	fichecesure = models.BooleanField(default = True, blank = True)
	fichebourse = models.BooleanField(default = True, blank = True)
	fichereglement = models.BooleanField(default = True, blank = True)

	def __str__(self):
		return self.etablissement.__str__()

	def all_fiche(self):
		"""Retourne les fiches choisies par l'établissement"""
		return [fiche for fiche in all_fiche if getattr(self, fiche.__name__.lower())]

	@staticmethod
	def get(etablissement):
		"""Crée, si nécessaire, et retourne l'objet selectfiches lié à un établissement"""
		try:
			return SelectFiches.objects.get(etablissement = etablissement)
		except SelectFiches.DoesNotExist:
			parametres = SelectFiches(etablissement = etablissement)
			parametres.save()
			return parametres

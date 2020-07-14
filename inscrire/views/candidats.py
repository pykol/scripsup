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

from collections import namedtuple

from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.views.generic import TemplateView, DetailView, UpdateView, \
		View
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, render
from django.urls import reverse
from django.template.loader import select_template, render_to_string
from django.contrib.contenttypes.models import ContentType
from django.views.generic.detail import SingleObjectMixin
from django.core.mail import send_mail

from inscrire.models import ResponsableLegal, Candidat, ParcoursupUser
from inscrire.models.fiches import Fiche, all_fiche
from inscrire.forms.fiches import candidat_form
from .permissions import AccessPersonnelMixin, AccessGestionnaireMixin


class ResponsableLegal(AccessPersonnelMixin, DetailView):
	"""
	Affiche les informations personnelles d'un responsable légal
	"""
	model = ResponsableLegal
	template_name = "responsablelegal.html"
	context_object_name = "responsablelegal"

class CandidatFicheMixin:
	"""
	Mixin qui ajoute au contexte la liste des fiches d'inscription que
	le candidat doit remplir.
	"""
	def get_fiches(self):
		"""
		Construction de la liste des fiches.

		Ces fiches peuvent être attachées à des formulaires d'édition.
		Chaque formulaire est initialisé, dans le cas d'une requête
		POST, avec les données soumises.
		"""
		# Ajout des fiches applicables
		FicheTpl = namedtuple('FicheTpl', ('fiche', 'form', 'template'))
		fiches = []
		candidat = self.object
		etablissement = candidat.voeu_actuel.formation.etablissement
		for fiche in candidat.fiche_set.filter(polymorphic_ctype__in = etablissement.fiches.all()).exclude(etat=Fiche.ETAT_ANNULEE):
			try:
				if self.request.method in ('POST', 'PUT'):
					form = candidat_form[type(fiche)](instance=fiche,
							data=self.request.POST,
							files=self.request.FILES)
				else:
					form = candidat_form[type(fiche)](instance=fiche)
			except:
				form = None


			templates = [
				'fiche/{}_gestionnaire.html'.format(fiche._meta.model_name),
				'fiche/fiche_base_gestionnaire.html'
						] if self.request.user.est_gestionnaire() else [
				'fiche/{}_candidat.html'.format(fiche._meta.model_name),
									'fiche/fiche_base_candidat.html'
								]
			fiches.append(FicheTpl(
				fiche=fiche,
				form=form,
				template=select_template(templates)
				))
		fiches.sort(key=lambda fiche:
				all_fiche.index(type(fiche.fiche)))
		return fiches

	def get_context_data(self, **kwargs):
		"""
		Ajout des fiches au contexte. Ces fiches sont créées par un
		appel à la méthode get_fiches sauf si elles sont déjà passées en
		paramètre (ce qui se produit par exemple lors d'un POST qui a
		signalé des erreurs de traitement).
		"""
		context = super().get_context_data()
		context['fiches'] = kwargs.get('fiches', self.get_fiches())
		return context

class CandidatDetail(AccessPersonnelMixin, CandidatFicheMixin, DetailView):
	"""
	Affiche les informations personnelles d'un candidat, à destination
	des personnels de l'établissement.
	"""
	model = Candidat
	context_object_name = 'candidat'

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		context["nombre_responsables"] = self.object.responsables.count()
		context['voeu'] = self.object.voeu_actuel
		context['etablissement_origine'] = self.get_object().get_fiche('fichescolariteanterieure').etablissement
		return context

	def post(self, request, *args, **kwargs):
		"""- Il y a un formulaire par fiche plus, le cas échéant, un formulaire
		 	permettant de valider d'un coup toutes les fiches.
			Les différents formulaires sont identifiés par la valeur du bouton
			(Valider toutes les fiches, Valider, Editer, Enregistrer) et le champ
			caché 'fiche'.
		   - Editer remet la fiche dans l'état ETAT_EDITION
		   - Valider met  la fiche dans l'état ETAT_TERMINEE
		   - Enregistrer enregistre les données du formulaire
		"""
		if not request.user.is_authenticated:
			return self.handle_no_permission() # capturer une connexion interrompue
		candidat = self.get_object()
		data = request.POST
		if data['fonction'] == 'Valider toutes les fiches':
			Fiche.objects.filter(candidat=candidat, etat=Fiche.ETAT_CONFIRMEE,
				polymorphic_ctype__in = candidat.voeu_actuel.formation.etablissement.fiches.all()).update(etat=Fiche.ETAT_TERMINEE)
			return redirect(reverse('candidat_detail',
				args=[candidat.dossier_parcoursup]))

		if data['fonction'] == 'Photo inexploitable':
			return render(request, 'inscrire/photo_inexploitable_confirm.html', {'candidat': candidat})
		fiche = Fiche.objects.get(pk=int(data['fiche']))

		if data['fonction'] == 'Valider':
			fiche.etat = fiche.ETAT_TERMINEE
			fiche.save()
		elif data['fonction'] == 'Confirmer':
			fiche.etat = fiche.ETAT_CONFIRMEE
			fiche.save()
		elif data['fonction'] == 'Éditer':
			fiche.etat = fiche.ETAT_EDITION
			fiche.save()
		elif data['fonction'] == 'Enregistrer':
			form = candidat_form[type(fiche)](instance=fiche,
							data=data,
							files=self.request.FILES)
			if form.is_valid():
				form.save()
		return redirect(reverse('candidat_detail',
			args=[candidat.dossier_parcoursup])+'#fiche_{}'.format(fiche.pk))


class CandidatUpdate(AccessGestionnaireMixin, CandidatFicheMixin, UpdateView):
	"""
	Permet la modification des informations personnelles par les
	gestionnaires du lycée.
	"""
	model = Candidat
	fields = ['adresse', 'telephone', 'telephone_mobile', 'date_naissance', 'genre']
	template_name = "candidat_update.html"
	success_url = "/candidat"

	def post(self, request, *args, **kwargs):
		pass

class CandidatDossier(AccessPersonnelMixin, DetailView):
	"""
	Affiche le dossier final du candidat.
	"""
	model = Candidat
	template_name = 'inscrire/dossier/dossier.html'

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		context["candidat"] = self.object
		context["voeu"] = self.object.voeu_actuel

		# Fiches d'inscription
		fiches = self.object.fiche_set.filter(
				etat__in=(Fiche.ETAT_EDITION, Fiche.ETAT_CONFIRMEE, Fiche.ETAT_TERMINEE))
		context['fiche_list'] = sorted(fiches,
				key=lambda fiche: all_fiche.index(type(fiche)))
		for fiche in fiches:
			context[fiche._meta.model_name] = fiche
		return context

class ParcoursupSynchroManuelle(AccessGestionnaireMixin, View):
	def post(self, request, *args, **kwargs):
		for psup_user in ParcoursupUser.objects.filter(
				etablissement__inscriptions=True):
			psup_user.get_candidats_admis()
		return redirect('home')

class ParcoursupDemissions(AccessGestionnaireMixin, View):
	def post(self, request, *args, **kwargs):
		for psup_user in ParcoursupUser.objects.filter(
				etablissement__inscriptions=True):
			psup_user.demissions()
		return redirect('home')


class PhotoInexploitable(AccessGestionnaireMixin, View):
	def post(self, request, *args, **kwargs):
		candidat = Candidat.objects.get(pk = kwargs['pk'])
		fiche_identite = candidat.get_fiche('ficheidentite')
		fiche_identite.photo = None
		fiche_identite.etat=fiche_identite.ETAT_EDITION
		fiche_identite.save()
		message = "Photographie supprimée"
		voeu_actuel = candidat.voeu_actuel
		render_context = {
				'candidat': candidat,
				'etablissement': voeu_actuel.formation.etablissement,
				'voeu': voeu_actuel,
				}
		ok=send_mail(
				render_to_string('inscrire/email_photographie_inexploitable_subject.txt',
					context=render_context).strip(),
				render_to_string('inscrire/email_photographie_inexploitable_message.txt',
					context=render_context).strip(),
				"{email}".format(
					email=voeu_actuel.formation.etablissement.email_technique),
				("{candidat_prenom} {candidat_nom} <{email}>".format(
					candidat_prenom=str(candidat.user.first_name),
					candidat_nom=str(candidat.user.last_name),
					email=str(candidat.user.email)),),
				html_message=render_to_string('inscrire/email_photographie_inexploitable_message.html',
					context=render_context).strip()
			)
		if ok:
			message += " et mail envoyé."
			messages.success(request, message)
		else:
			message += " mais le mail n'a pas pu être envoyé. Contactez le candidat."
			messages.error(request, message)
		return redirect(reverse('candidat_detail', args=[candidat.dossier_parcoursup]))

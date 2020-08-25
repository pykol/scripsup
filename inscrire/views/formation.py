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

import csv, io
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, View, FormView
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.db.models import Value
from django.db import models

from inscrire.models import Formation, Candidat, Voeu, MefOption, Classement
from .permissions import AccessDirectionMixin, AccessGestionnaireMixin
from inscrire.forms.parametrage import OptionActiverFormset, \
		FormationForm
from inscrire.forms.formation import ImportParcoursupForm, ImportClassementForm

class FormationListView(AccessDirectionMixin, ListView):
	model = Formation

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		context['import_manuel_form'] = ImportParcoursupForm()
		return context

class FormationDetailView(AccessDirectionMixin, DetailView):
	model = Formation

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		candidats_etat_edition = self.object.candidats_etat_edition().annotate(
			etat_dossier=Value("Edition", output_field=models.CharField()))
		candidats_etat_complet = self.object.candidats_etat_complet().annotate(
			etat_dossier=Value("Complet", output_field=models.CharField()))
		candidats_etat_termine = self.object.candidats_etat_termine().annotate(
			etat_dossier=Value("Termine", output_field=models.CharField()))
		candidats_etat_demission = self.object.candidats_etat_demission().annotate(
			etat_dossier=Value("Démission", output_field=models.CharField()))

		context["candidat_list"] = candidats_etat_edition.union(candidats_etat_complet,
			candidats_etat_termine, candidats_etat_demission).order_by('last_name', 'first_name')
		context['formation_form'] = FormationForm(prefix='formation',
				instance=self.object)
		context['option_formset'] = OptionActiverFormset(prefix='options',
				instance=self.object,
				queryset=MefOption.objects.order_by('modalite', 'rang',
					'matiere__libelle_court'))
		return context

class FormationUpdateView(AccessDirectionMixin, SingleObjectMixin, View):
	model = Formation

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		formation_form = FormationForm(data=self.request.POST,
				instance=self.object,
				prefix='formation')
		if formation_form.is_valid():
			formation_form.save()
		option_formset = OptionActiverFormset(prefix='options',
				instance=self.object, data=self.request.POST)
		if option_formset.is_valid():
			option_formset.save()

		return redirect('formation_detail', slug=self.object.slug)


class ImportParcoursupView(AccessGestionnaireMixin, FormView):
	form_class = ImportParcoursupForm

	def form_valid(self, form):
		propositions = form.propositions()
		psup_user = form.cleaned_data['formation'].etablissement.parcoursupuser
		for proposition in propositions:
			candidat = psup_user.import_candidat(proposition)
			candidat.email_bienvenue(self.request)
		return super().form_valid(form)

	def get_success_url(self):
		return reverse('formation_list')


class ImportClassementView(AccessGestionnaireMixin, FormView):
	form_class=ImportClassementForm

	def form_valid(self, form):
		formation=form.cleaned_data['formation']
		fichier=form.cleaned_data['fichier']
		data=fichier.read().decode("utf8")
		io_string = io.StringIO(data)
		reader=csv.reader(io_string, delimiter=";")
		entete=next(reader)
		if entete[0] != "Classement" or entete[1] not in ["Numéro", "Numero"]:
			form.add_error("fichier", "La ligne d'entête doit être 'Classement;Numéro'")
			return self.form_invalid(form)
		classements=Classement.objects.filter(formation=formation)
		classements.delete()
		voeux=Voeu.objects.filter(formation=formation)
		voeux.update(_classement=None)
		liste_classements=[]
		for ligne in reader:
			try:
				int(ligne[0]) # on vérifie que le candidat est classé
				liste_classements.append(Classement(dossier_parcoursup=ligne[1], classement=ligne[0], formation=formation))
			except ValueError:
				pass
		Classement.objects.bulk_create(liste_classements)
		return super().form_valid(form)

	def get_success_url(self):
		return reverse('formation_list')


class ExportCandidatsAdmisView(AccessDirectionMixin, DetailView):
	model=Formation

	def get(self, request, *args, **kwargs):
		formation=self.get_object()
		candidats_etat_edition = formation.candidats_etat_edition().annotate(
			etat_dossier=Value("Edition", output_field=models.CharField()))
		candidats_etat_complet = formation.candidats_etat_complet().annotate(
			etat_dossier=Value("Complet", output_field=models.CharField()))
		candidats_etat_termine = formation.candidats_etat_termine().annotate(
			etat_dossier=Value("Termine", output_field=models.CharField()))
		candidats_etat_demission = formation.candidats_etat_demission().annotate(
			etat_dossier=Value("Démission", output_field=models.CharField()))
		candidats=candidats_etat_edition.union(candidats_etat_complet,
			candidats_etat_termine, candidats_etat_demission).order_by('last_name', 'first_name')

		reponse  = HttpResponse(content_type='text/csv')
		reponse['Content-Disposition'] = 'attachment; filename = admis_{}.csv'.format(formation.slug)
		writer = csv.writer(reponse, delimiter  = ';')
		entete=[
				'Parcoursup',
				'Classement',
				'Nom',
				'Prénom',
				'INE',
				'Etat',
				'Dernière connexion',
				'Internat',
				'Genre',
				'Email',
				'Téléphone',
				'Mobile',
				'Adresse',
				'Série Bac',
				'Mention Bac'
			]
		rangs_obligatoires=list(set(formation.mefoption_set.filter(
			modalite=MefOption.MODALITE_OBLIGATOIRE,
			inscriptions=True).values_list('rang',
					flat=True)))
		rangs_obligatoires.sort()
		for r in rangs_obligatoires:
			entete.append("Option obligatoire (rang {})".format(r))
		for r in range(1, 7):
			entete.append("Option facultative {}".format(r))
		writer.writerow(entete)
		for candidat in candidats:
			voeu=candidat.voeu(formation)
			ligne=[
					candidat.dossier_parcoursup,
					voeu.classement,
					candidat.last_name, candidat.first_name,
					candidat.ine, candidat.etat_dossier,
					candidat.user.last_login.strftime("%Y-%m-%d") if candidat.user.last_login else "",
					voeu.internat,
					candidat.genre_court(),
					candidat.user.email,
					candidat.telephone,
					candidat.telephone_mobile,
					candidat.adresse,
					candidat.bac_serie,
					candidat.bac_mention_court()
				]
			fichescolarite=candidat.get_fiche('fichescolarite', etat=FICHE.ETAT_CONFIRMEE)
			if fichescolarite:
				for r in rangs_obligatoires:
					try:
						mefoption=fichescolarite.options.get(formation=formation, rang=r)
						ligne.append(mefoption.__str__())
					except MefOption.DoesNotExist:
						ligne.append("")
				for mefoption in fichescolarite.options.filter(formation=formation, modalite=MefOption.MODALITE_FACULTATIVE):
					ligne.append(mefoption.__str__())
			writer.writerow(ligne)
		return reponse

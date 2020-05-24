from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView, DetailView, UpdateView
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from django.template.loader import select_template

from inscrire.models import ResponsableLegal, Candidat
from inscrire.models.fiches import Fiche
USER = get_user_model()

def set_candidat(_dispatch):
	"""décorateur de dispatch; vérifie que l'utilisateur est un candidat et renseigne self.candidat"""

	def dispatch(self, request, *args, **kwargs):
		user = request.user
		try:
			candidat = user.candidat
			self.candidat = candidat
		except USER.candidat.RelatedObjectDoesNotExist:
			return redirect("/")
		return _dispatch(self, request,*args, **kwargs)
	return dispatch


@method_decorator(login_required, name='dispatch')
class CandidatDetail(TemplateView):
	"""Affiche les informations personnelles d'un candidat"""

	template_name = "candidat.html"

	@set_candidat
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		context["candidat"] = self.candidat
		context["nombre_responsables"] = self.candidat.responsables.count()
		return context


@method_decorator(login_required, name='dispatch')
class ResponsableLegal(DetailView):
	"""Affiche les informations personnelles d'un responsable légal"""

	model = ResponsableLegal
	template_name = "responsablelegal.html"
	context_object_name = "responsablelegal"

	@set_candidat
	def dispatch(self, request, *args, **kwargs):
		"""Vérifie que le responsable à afficher est lié au candidat connecté"""
		pk_responsables = self.candidat.responsables.values_list("pk", flat = True)
		if not kwargs["pk"] in pk_responsables:
			return redirect("/")
		return super().dispatch(request, *args, **kwargs)


class CandidatUpdate(UpdateView):
	"""Permet la modification des informations personnelles"""

	model = Candidat
	fields = ['adresse', 'telephone', 'telephone_mobile', 'date_naissance', 'genre']
	template_name = "candidat_update.html"
	success_url = "/candidat"

	@set_candidat
	def dispatch(self, request, *args, **kwargs):
		"""compare le numero de dossier appelé et celui du candidat connecté"""
		if kwargs['pk'] != self.candidat.pk:
			return redirect("/")
		return super().dispatch(request, *args, **kwargs)

	# TODO ceci envoie les formulaires dans le contexte, mais ils ne
	# sont pour l'instant pas traités par POST
	def get_context_data(self):
		context = super().get_context_data()

		# Ajout des fiches applicables
		FicheTpl = namedtuple('FicheTpl', ('fiche', 'form', 'template'))
		fiches = []
		for fiche in self.object.fiche_set.exclude(etat=Fiche.ETAT_ANNULEE):
			fiches.append(FicheTpl(
				fiche=fiche,
				form=forms.fiches[type(fiche)](),
				template=select_template(
					[
						'fiche/{}_candidat.html'.format(fiche._meta.model_name),
						'fiche/fiche_base_candidat.html'
					])
				))
		context['fiches'] = fiches
		return context

from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView, DetailView
from django.utils.decorators import method_decorator
from django.shortcuts import redirect

from inscrire.models import ResponsableLegal
USER = get_user_model()

@method_decorator(login_required, name='dispatch')
class Candidat(TemplateView):
    """Affiche les informations personnelles d'un candidat"""

    template_name = "candidat.html"

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        try:
            candidat = user.candidat
            self.candidat = candidat
        except USER.candidat.RelatedObjectDoesNotExist:
            return redirect("/")
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

    def dispatch(self, request, *args, **kwargs):
        """On vérifie que le responsable à afficher est lié au candidat connecté"""
        user = request.user
        try:
            candidat = user.candidat
            self.candidat = candidat
        except USER.candidat.RelatedObjectDoesNotExist:
            return redirect("/")
        pk_responsables = candidat.responsables.values_list("pk", flat = True)
        if not kwargs["pk"] in pk_responsables:
            return redirect("/")
        return super().dispatch(request, *args, **kwargs)

from django.views.generic import ListView, DetailView, View, FormView
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from inscrire.models import Mailing
from inscrire.forms.mailing import MailingForm
from .permissions import AccessDirectionMixin

class MailingView(AccessDirectionMixin, FormView):
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy('mailing_list')

    def setup(self, request, *args, **kwargs):
        """Initialise self.mailing"""
        super().setup(request, *args, **kwargs)
        try:
            self.mailing=Mailing.objects.get(pk=self.kwargs.get('pk'))
        except Mailing.DoesNotExist:
            self.mailing=None

    def get_context_data(self, *args, **kwargs):
        context=super().get_context_data(*args, **kwargs)
        context["mailing"] = self.mailing
        return context

    def get_form(self):
        if self.request.method=="GET":
            if self.mailing: # mise à jour d'un mailing existant
                return self.get_form_class()(instance=self.mailing)
            else:
                initial={}
                initial.update({"de": self.request.user.email})
                initial.update({"repondre_a": self.request.user.email})
                return self.get_form_class()(initial=initial)
        else:
            if self.mailing:
                return self.get_form_class()(self.request.POST, instance=self.mailing)
            else:
                return self.get_form_class()(self.request.POST)


    def form_valid(self, form):
        form.save(commit = True)
        if self.request.POST["fonction"] == "Envoyer":
            mailing=form.instance
            mailing.send()
        return redirect(self.get_success_url())


class MailingList(AccessDirectionMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = 'mailings'

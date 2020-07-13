from django.db import models
from django.core.mail import EmailMessage

from inscrire.models import Formation, Etablissement, Candidat, ResponsableLegal, Voeu

class Mailing(models.Model):
    EDITION, COMPLET, TERMINE = 1, 2, 3
    CHOIX_ETAT_DOSSIER = [(EDITION, "Édition"), (COMPLET, "Complet"), (TERMINE, "Terminé")]

    brouillon = models.BooleanField(default = True)
    de = models.EmailField()
    repondre_a = models.EmailField()
    copie_responsables = models.BooleanField(default = False,
        help_text="Cocher pour envoyer une copie aux responsables légaux")
    formation = models.ForeignKey(Formation, null=True, blank=True,
        on_delete = models.SET_NULL,
        help_text="Envoyer aux candidats de cette formation")
    etablissement = models.ForeignKey(Etablissement, null=True, blank=True,
        on_delete = models.SET_NULL,
        help_text="Envoyer aux candidats de cet établissement (si formation non choisie)")
    etat_dossier = models.PositiveSmallIntegerField(choices = CHOIX_ETAT_DOSSIER, default= None,
        null=True,  blank=True,
        help_text = "N'envoyer qu'aux candidats dont le dossier est dans l'état indiqué")
    connexion = models.NullBooleanField(default = None,
        help_text = "Envoyer à tous les candidats/ceux qui se sont connectés/ceux\
        qui ne se sont jamais connectés")
    derniere_connexion_avant = models.DateTimeField(null=True, default = None, blank = True,
        help_text = "N'envoyer que si le candidat ne s'est pas connecté depuis cette date")
    derniere_connexion_apres = models.DateTimeField(null=True, default = None, blank = True,
        help_text = "N'envoyer que si le candidat s'est connecté depuis cette date")
    internat = models.NullBooleanField(default = None,
        help_text = "Envoyer à tous les candidats/ceux qui sont sur un voeu\
        avec internat/sans internat")
    sujet=models.CharField(max_length=200)
    message = models.TextField()
    candidats = models.ManyToManyField(Candidat, through='Envoi') # candidats à qui le mail a été envoyé

    def send(self):
        if self.formation:
            formation=self.formation
            if self.etat_dossier==self.EDITION:
                candidats=formation.candidats_etat_edition()
            elif self.etat_dossier==self.COMPLET:
                candidats=formation.candidats_etat_complet()
            elif self.etat_dossier==self.TERMINE:
                candidats=formation.candidats_etat_termine()
            else:
                voeux = Voeu.objects.filter(formation = self.formation)
                candidats=Candidat.objects.filter(voeu__in = voeux)
        else:
            etablissement=self.etablissement
            if self.etat_dossier==self.EDITION:
                candidats=etablissement.candidats_etat_edition()
            elif self.etat_dossier==self.COMPLET:
                candidats=etablissement.candidats_etat_complet()
            elif self.etat_dossier==self.TERMINE:
                candidats=etablissement.candidats_etat_termine()
            else:
                voeux = Voeu.objects.filter(formation__etablissement = self.etablissement)
                candidats=Candidat.objects.filter(voeu__in = voeux)
        if self.internat != None:
            voeux = voeux.filter(internat = self.internat)
        # On n'envoie le mail qu'aux candidats qui ne l'ont pas déjà reçu
        candidats = candidats.difference(self.candidats.all())
        if self.derniere_connexion_apres:
            # candidats.filter(...) dysfonctionne !
            candidats = candidats.intersection(Candidat.objects.filter(user__last_login__gte = self.derniere_connexion_apres))
        if self.derniere_connexion_avant:
            candidats = candidats.intersection(Candidat.objects.filter(models.Q(user__last_login__isnull = True)|models.Q(user__last_login__lte = self.derniere_connexion_avant)))
        if self.connexion != None:
            if self.connexion:
                candidats = candidats.intersection(Candidat.objects.filter(user__last_login__isnull = False))
            else:
                candidats = candidats.intersection(Candidat.objects.filter(user__last_login__isnull = True))
        un_envoi = False
        for candidat in candidats:
            if self.copie_responsables:
                cc = [responsable.email for responsable in candidat.responsables.all() if responsable.email]
            else:
                cc = []
            email = EmailMessage(
                subject=self.sujet,
                body=self.message,
                from_email = self.de,
                to =[candidat.user.email,],
                cc = cc,
                reply_to = (self.repondre_a,)
            )
            ok = email.send()
            if ok:
                un_envoi = True
                envoi = Envoi(mailing = self, candidat = candidat)
                envoi.save()
                if self.copie_responsables:
                    envoi.responsables.add(*candidat.responsables.exclude(email="").exclude(email__isnull = True).values_list('id', flat=True))
        if un_envoi:
            self.brouillon = False
            self.save()


class Envoi(models.Model):
    mailing = models.ForeignKey(Mailing, on_delete = models.CASCADE)
    candidat = models.ForeignKey(Candidat, on_delete = models.CASCADE)
    date = models.DateTimeField(auto_now_add = True)
    responsables = models.ManyToManyField(ResponsableLegal) # responsables légaux à qui le mail à été envoyé

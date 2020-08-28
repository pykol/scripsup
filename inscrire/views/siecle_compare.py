# Pour comparaison avec les données élèves de SIECLE
# Fonctionnalité très grosièrement développée


from django.shortcuts import render
from django.views.generic import FormView
from inscrire.forms.siecle_compare import ImportFichiersSiecleForm
from inscrire.lib.siecle.fichiers_siecle_compare import ElevesSansAdresses, Structures
from .permissions import AccessGestionnaireMixin
from inscrire.models import Formation, Candidat, Etablissement, MefMatiere

class CompareView(AccessGestionnaireMixin, FormView):
    form_class=ImportFichiersSiecleForm
    template_name="inscrire/siecle_compare_form.html"

    def form_valid(self, form):
        cd=form.cleaned_data
        elevessansadresses=cd['elevessansadresses']
#        elevesavecadresses=cd['elevesavecadresses']
        structures=cd['structures']
        if elevessansadresses:
            eleves=ElevesSansAdresses(elevessansadresses).eleves()
        structures=Structures(structures)
        etablissement=Etablissement.objects.get(numero_uai=structures.parametres()['uai'])
        structures=structures.structures()
        mefs_scripsup = dict()
        for formation in Formation.objects.filter(etablissement=etablissement):
            if formation.code_mef[-2]=='1': #
                mefs_scripsup[formation.code_mef]=formation
        divisions=set()
        for mef in mefs_scripsup:
            divisions.update(structures[mef])
        for eleve, dic in eleves.copy().items(): # suppression des élèves appartenant à une division non concernée
            if dic['structure'] not in divisions:
                eleves.pop(eleve)
        eleves_sans_candidat={}
        for eleve, dic in eleves.items(): # identification du candidat associé
            try:
                if not dic['email']:
                    raise Candidat.DoesNotExist
                candidat=Candidat.objects.get(user__email=dic['email'])
                dic['candidat']=candidat
            except Candidat.DoesNotExist:
                try:
                    if not dic['ine']:
                        raise Candidat.DoesNotExist
                    candidat=Candidat.objects.get(ine=dic['ine'])
                    dic['candidat']=candidat
                except Candidat.DoesNotExist:
                    eleves_sans_candidat[eleve]=dic
                    dic['candidat']=None
        for eleve in eleves_sans_candidat:
            eleves.pop(eleve)
        pk_candidats=[dic['candidat'].pk for eleve, dic in eleves.items()]
        candidats_sans_eleve=etablissement.candidats.exclude(pk__in=pk_candidats)
        context={
            'eleves_sans_candidat':eleves_sans_candidat,
            'candidats_sans_eleve':candidats_sans_eleve,
        }
        # divergences d'options
        candidats=[]
        for eleve, dic in eleves.items():
            candidat=dic['candidat']
            fichescolarite=candidat.get_fiche('fichescolarite')
            options=fichescolarite.options.all()
            matieres=[option.matiere.code for option in options]
            options_siecle_pas_scripsup=[]
            for option in dic['options']:
                if option['code_matiere'] not in matieres:
                    options_siecle_pas_scripsup.append(MefMatiere.objects.get(code=option['code_matiere']).libelle_court)
            if options_siecle_pas_scripsup:
                candidats.append([candidat, dic['structure'], options_siecle_pas_scripsup])
        context['divergences_siecle_scripsup']=candidats

        return render(self.request, "inscrire/siecle_compare.html", context)

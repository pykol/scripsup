from django import forms
from inscrire.models import Mailing, Etablissement

class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['de', 'repondre_a', 'copie_responsables', 'etablissement',
            'formation', 'etat_dossier', 'connexion', 'derniere_connexion_avant',
            'derniere_connexion_apres', 'internat', 'sujet', 'message']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['etablissement'].queryset = Etablissement.objects.filter(inscriptions=True)
        if 'instance' in kwargs and not kwargs['instance'].brouillon:
            self.fields.pop("de")
            self.fields.pop("repondre_a")
            self.fields.pop("sujet")
            self.fields.pop("message")

    def clean(self):
        cd = super().clean()
        etablissement = cd['etablissement']
        formation =cd['formation']
        if not etablissement and not formation:
            raise forms.ValidationError("Indiquez l'établissement ou la formation")
        if cd['derniere_connexion_apres'] > cd['derniere_connexion_avant']:
            raise forms.ValidationError("Vos dates de connexion sont incohérentes")

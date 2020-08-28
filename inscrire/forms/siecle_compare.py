# Pour comparaison avec les données élèves de SIECLE
# Fonctionnalité très grosièrement développée

from django import forms
class ImportFichiersSiecleForm(forms.Form):
    structures=forms.FileField(label="Structures.xml")
    elevessansadresses=forms.FileField(label="ElevesSansAdresses.xml", required=False) #la faute d'orthographe, c'est SIECLE !
#    elevesavecadresses=forms.FileField(label="ElevesAvecAdresses.xml", required=False)
#    responsablessansadresses=forms.FileField(label="ResponsablesSansdAdresses.xml", required=False)
#    responsablesavecadresses=forms.FileField(label="ResponsablesAvecAdresses.xml", required=False)

    def clean(self):
        cd=super().clean()
        # si l'un des noms de fichiers ne correspondait pas, clean_nom a provoqué
        # la suppression du champs du cleaned_data
        if (not 'structures' in cd) or (not 'elevessansadresses' in cd):
    #         or (not 'elevesavecadresses' in cd)\
    #        or (not 'responsablessansadresses' in cd) or (not 'responsablesavecadresses' in cd)\
            return
        elevessansadresses=cd.get('elevessansadresses', None)
    #    elevesavecadresses=cd.get('elevesavecadresses', None)
        if not elevessansadresses and not elevesavecadresses:
            raise forms.ValidationError("Fournissez obligatoirement l'un des fichiers élèves")

    def clean_structures(self):
        fichier=self.cleaned_data['structures']
        if fichier and fichier.name != 'Structures.xml':
            raise forms.ValidationError("Le nom du fichier ne correspond pas.")
        return fichier

    def clean_elevessansadresses(self):
        fichier=self.cleaned_data['elevessansadresses']
        if fichier and fichier.name != 'ElevesSansAdresses.xml':
            raise forms.ValidationError("Le nom du fichier ne correspond pas.")
        return fichier

    # def clean_elevesavecadresses(self):
    #     fichier=self.cleaned_data['elevesavecadresses']
    #     if fichier and fichier.name != 'ElevesAvecAdresses.xml':
    #         raise forms.ValidationError("Le nom du fichier ne correspond pas.")
    #     return fichier
    #
    # def clean_responsablessansadresses(self):
    #     fichier=self.cleaned_data['responsablessansadresses']
    #     if fichier and fichier.name != 'ResponsablesSansAdresses.xml':
    #         raise forms.ValidationError("Le nom du fichier ne correspond pas.")
    #     return fichier
    #
    # def clean_responsablesavecadresses(self):
    #     fichier=self.cleaned_data['responsablesavecadresses']
    #     if fichier and fichier.name != 'ResponsablesAvecAdresses.xml':
    #         raise forms.ValidationError("Le nom du fichier ne correspond pas.")
    #     return fichier

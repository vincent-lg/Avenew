from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField(label="Le fichier YML à appliquer")

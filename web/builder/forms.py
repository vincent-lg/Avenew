from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField(label="The YML file to upload")

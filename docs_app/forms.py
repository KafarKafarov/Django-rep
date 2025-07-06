from django import forms
from .models import Docs


class UploadForm(forms.Form):
    file = forms.FileField(label='Выберите файл')



class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Docs
        fields = ['file_path']
from django import forms

class BulkUploadForm(forms.Form):
    excel_file = forms.FileField()
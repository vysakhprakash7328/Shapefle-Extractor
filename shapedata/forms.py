from django import forms

class UploadFileForm(forms.Form):
    
    file = forms.FileField()

class db_connForm(forms.Form):
    db_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    db_user = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    db_pass = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    db_host = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    db_port = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control'}))
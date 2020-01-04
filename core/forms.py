from django import forms
from core.models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class StartUpsForm(UserCreationForm):
    email = forms.EmailField(max_length=150)
    POC = POC = forms.CharField(max_length=50, label='Point Of Contact')
    class Meta():
        model = User
        fields = ('username','email','POC','password1', 'password2',)    

class StudentsForm(UserCreationForm):
    name = forms.CharField(max_length=100)
    roll_number = forms.IntegerField(label='IITG Roll Number')
    phone_number = forms.RegexField(regex=r'^\d{9,10}$')
    email = forms.EmailField(max_length=150)
    class Meta():
        model = User
        fields = ('name','username','email','roll_number','password1', 'password2',)   

class ApplicationForm(forms.Form):
    resume = forms.FileField()
    content = forms.CharField(max_length=100)

class LogoForm(forms.Form):
    logo = forms.ImageField()
    

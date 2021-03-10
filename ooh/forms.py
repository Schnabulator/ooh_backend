from django import forms


from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import OohUser

class OohUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = OohUser
        # All fields, that have to be saved --> update for location! //TODO
        fields = ('email', 'firstname', 'lastname', 'birthday', )


class OohUserChangeForm(UserChangeForm):
    class Meta:
        model = OohUser
        fields = ('email',)

class RegLoginSwitch(forms.Form):
    formular = forms.CharField()

class UserLoginForm(forms.Form):
    # user = forms.CharField(required=False)
    email = forms.EmailField()
    password1 = forms.CharField(max_length=32, widget=forms.PasswordInput)

class UserRegisterForm(UserCreationForm):
    firstname = forms.CharField(required=False)
    lastname =  forms.CharField(required=False)
    email = forms.EmailField()
    password = forms.CharField(max_length=32, widget=forms.PasswordInput)
    plz  = forms.CharField(required=True)
    cityname = forms.CharField(required=True)
    street = forms.CharField(required=True)
    housenumber = forms.IntegerField()

class UserLocation(forms.Form):
    data = forms.CharField(required=True)
    plz  = forms.CharField(required=True)
    cityname = forms.CharField(required=True)
    street = forms.CharField(required=True)
    housenumber = forms.IntegerField()
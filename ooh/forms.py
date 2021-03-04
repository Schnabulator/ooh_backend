from django import forms


from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import OohUser

class OohUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = OohUser
        fields = ('email',)


class OohUserChangeForm(UserChangeForm):
    class Meta:
        model = OohUser
        fields = ('email',)

class RegLoginSwitch(forms.Form):
    formular = forms.CharField()

class UserLoginForm(forms.Form):
    # user = forms.CharField(required=False)
    email = forms.EmailField()
    passwd = forms.CharField(max_length=32, widget=forms.PasswordInput)

class UserRegisterForm(forms.Form):
    user = forms.CharField(required=False)
    email = forms.EmailField()
    passwd = forms.CharField(max_length=32, widget=forms.PasswordInput)
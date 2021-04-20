from django import forms


from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import OohUser, EventCategory

class OohUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = OohUser
        # All fields, that have to be saved --> update for location! //TODO
        fields = ('email', 'firstname', 'lastname', 'birthday', 'street', 'housenumber')

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

class UserLocation(forms.Form):
    data = forms.CharField(required=True)
    plz  = forms.CharField(required=True)
    cityname = forms.CharField(required=True)
    street = forms.CharField(required=True)
    housenumber = forms.IntegerField()

class AddEvent(forms.Form):
    # Location 
    locationName = forms.CharField(required=True)
    locationType = forms.CharField(required=True)
    cityname = forms.CharField(required=True)
    plz = forms.CharField(required=True, max_length=10)
    street = forms.CharField(required=True)
    room = forms.CharField(required=False)

    # EventTemplate itself
    desciption = forms.CharField(required=True)
    eventName = forms.CharField(required=True)
    picture = forms.ImageField()
    pricecat = forms.IntegerField()
    age = forms.IntegerField(required=False)
    specialcategory = forms.CharField(required=True)
    smoking = forms.CharField(required=False)
    # //TODO Categories maybe as commaseperated values (ala Tags)
    categories = forms.CharField(required=False)

    # Event
    starttime = forms.DateTimeField()
    endtime = forms.DateTimeField()
    intervalInDays = forms.IntegerField()

    # categories = forms.ModelMultipleChoiceField(queryset=EventCategory.objects.all(), widget=forms.CheckboxSelectMultiple)

class ParticipateForm(forms.Form):
    eventID = forms.IntegerField(required=True)
    probability = forms.IntegerField(required=False)

# //TODO create form for question and answer validation kaka


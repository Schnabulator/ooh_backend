from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import generic
from django.template import Context
from .models import Location, EventLocation, Event, OohUser, Participate
from .forms import UserLoginForm, UserRegisterForm, RegLoginSwitch
from django.contrib.auth import authenticate, login

from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView#, RegisterView


User = get_user_model()
# Create your views here.



def index(request):
    # return HttpResponse("Bämski Index.")
    context = {"body_id": "b_home"} #, "user": User}
    return render(request, 'ooh/index.html', context=context)

class UserLogoutView(LogoutView):
    pass

class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'ooh/login.html'
    def get(self, request, *args, **kwargs):
        context = {"body_id": "b_content"}
        return render(request, 'ooh/login.html', context=context)

    def post(self, request, *args, **kwargs):
        print("Login Post request.")
        form = RegLoginSwitch(request.POST)
        if form.is_valid():
            print("Form is valid!")
            
            if form.cleaned_data['formular'] == "reg":
                # Register handling
                form = UserRegisterForm(request.POST)
                if form.is_valid():
                    print("Register")
                    user = form.cleaned_data['email']
                    email = form.cleaned_data['email']
                    pw = form.cleaned_data['passwd']
                    user = create_user(username=user,password=pw, email=email)
                    if user is not None:
                        login(request)
                        print("Successful")
                else:
                    print(form.errors)
            elif form.cleaned_data['formular'] == "login":
                form = UserLoginForm(request.POST)
                if form.is_valid():
                    print("Login")
                    user = form.cleaned_data['email']
                    pw = form.cleaned_data['passwd']
                    user = authenticate(request,username=user,password=pw)
                    if user is not None:
                        # login(request)
                        print("Successful logged in "+ user.get_email())
                else:
                    print(form.errors)
        else: 
            print(form.errors)
        print(request.POST)

        return JsonResponse({'foo': 'bar'})
    

class EventLocationView(generic.ListView):
    template_name = 'ooh/eventlocations.html'
    context_object_name = 'near_eventlocations'
    def get_queryset(self):
        # return EventLocation.objects.filter(locationID__plz=68159)
        return EventLocation.objects.all
    
class EventView(generic.ListView):
    template_name = 'ooh/eventlocations.html'
    context_object_name = 'near_eventlocations'
    def get_queryset(self):
        # return EventLocation.objects.filter(locationID__plz=68159)
        return Event.objects.all

# class UserLoginView(generic.Loginview)
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views import generic
from django.template import Context
from .models import Location, EventLocation, Event, OohUser, Participate
from .forms import UserLoginForm, UserRegisterForm, RegLoginSwitch, OohUserCreationForm, UserLocation
from django.contrib.auth import authenticate, login

from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView #, RegisterView
from django.views.generic.edit import ProcessFormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


User = get_user_model()
# Create your views here.



def index(request):
    # return HttpResponse("Bämski Index.")
    context = {"body_id": "b_home"} #, "user": User}
    return render(request, 'ooh/index.html', context=context)

class UserLogoutView(LogoutView):
    template_name = 'ooh/logout.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class UserLoginView(LoginView, ProcessFormView):
    form_class = UserLoginForm
    template_name = 'ooh/login.html'

    def get(self, request, *args, **kwargs):
        context = {"body_id": "b_content"}
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        print("Login Post request.")
        form = RegLoginSwitch(request.POST)
        if form.is_valid():
            print("Form is valid!")
            
            if form.cleaned_data['formular'] == "reg":
                # Register handling
                print("Register")
                form = OohUserCreationForm(request.POST)
                if form.is_valid():
                    print("Valid form")
                    print(request.POST)
                    # user = form.cleaned_data['email']
                    # email = form.cleaned_data['email']
                    # pw = form.cleaned_data['passwd']
                    # user = create_user(username=user,password=pw, email=email)
                    # if user is not None:
                    #     login(request)
                    #     print("Successful")
                    form.save()
                    return JsonResponse({'success': 'Registrierung war erfolgreich.'})

                    # Cant Login user when he must confirm his email in future!
                    # email = form.cleaned_data.get('email')
                    # pw = form.cleaned_data.get('password1')
                    # user = authenticate(request,username=email,password=pw)
                    # if user is not None:
                    #     # login(request)
                    #     login(request, user)
                    #     print("Successful logged in and registered "+ user.email)
                    #     # return redirect('index')
                    #     return JsonResponse({'success': 'Registrierung war erfolgreich.'})
                    # else:
                    #     print("Hm.... user is None!")
                    #     return JsonResponse({'error': 'Login erfolglos.'})
                else:
                    print("ELSE")
                    print(form.errors)
            elif form.cleaned_data['formular'] == "login":
                # Login handler
                form = UserLoginForm(request.POST)
                if form.is_valid():
                    print("Login")
                    user = form.cleaned_data['email']
                    pw = form.cleaned_data['password1']
                    user = authenticate(request,username=user,password=pw)
                    if user is not None:
                        # login(request)
                        login(request,user)
                        print("Successful logged in "+ user.email)
                        # return redirect('index')
                        return JsonResponse({'success': 'Login war erfolgreich.'})
                    else:
                        print("User isnt authenticated")
                else:
                    print(form.errors)
            else:
                # non of reg or login handler
                print("Not login and reg")
        else: 
            print("Form error loginreg")
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
    template_name = 'ooh/events.html'
    context_object_name = 'near_eventlocations'
    def get_queryset(self):
        # return EventLocation.objects.filter(locationID__plz=68159)
        return Event.objects.all

# @method_decorator(login_required, name='as_view')
# class UserProfileView(generic.DetailView):
#     template_name = "ooh/profile.html"
#     def get_queryset(self):
#         return self.request.user

class UserProfile(generic.DetailView):
    template_name = "ooh/profile.html"
    
    @method_decorator(login_required(login_url="/profile/login"))
    def get(self, request, *args, **kwargs):
        # userloc = request.user.locationID
        context = {"body_id": "b_content"} 
        return render(self.request, template_name=self.template_name, context=context)

    @method_decorator(login_required(login_url="/profile/login"))
    def post(self, request, *args, **kwargs):
        form = UserLocation(request.POST)
        if form.is_valid():
            print("Valid Form for new location of user "+request.user.email)
            plz = form.cleaned_data['plz']
            cityname = form.cleaned_data['cityname']
            street = form.cleaned_data['street']
            housenumber = form.cleaned_data['housenumber']
            
            location = Location.objects.get(plz=plz, cityname=cityname)
            if(location is None):
                # //TODO Make a error message in se formular
                context = {"body_id": "b_content"} 
                return render(self.request, template_name=self.template_name, context=context)
            print(location)
            request.user.location = location
            request.user.street = street
            request.user.housenumber = housenumber
            request.user.save()
            pass
        context = {"body_id": "b_content"} 
        return render(self.request, template_name=self.template_name, context=context)
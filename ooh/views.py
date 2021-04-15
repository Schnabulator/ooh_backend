from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views import generic
from django.template import Context
from .models import Location, EventLocation, Event, OohUser, Participate, Question, ChoiceOption, UserSelection, EventCategory, LocationCategory
from .forms import UserLoginForm, RegLoginSwitch, OohUserCreationForm, UserLocation
from django.contrib.auth import authenticate, login
from django.db.models import Q


from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView #, RegisterView
from django.views.generic.edit import ProcessFormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import datetime

User = get_user_model()
# Create your views here.



# def index(request):
#     # return HttpResponse("Bämski Index.")
#     context = {"body_id": "b_home"} #, "user": User}
#     return render(request, 'ooh/index.html', context=context)

class index(generic.ListView):
    model = Event
    template_name = 'ooh/index.html'
    context_object_name = 'recommended_events'
    def get_queryset(self):
        # //TODO filter from user has to be set here!
        # User filter
        filt = UserSelection.objects.filter(user=self.request.user).filter(questionRun=self.request.user.currentQuestionRun).filter(valid=True)
        print("Filter {0}".format(filt.count()))
        objs = Event.objects.filter(Q(starttime__gte=datetime.date.today()))
        for f in filt:
            _cat = f.selection.text
            print(_cat)
            # get object for eventCategory
            # //TODO filter macht nur scheiße, fixen
            ecat = EventCategory.objects.filter(name__iexact=_cat)
            lcat = LocationCategory.objects.filter(name__iexact=_cat)
            print("Filterlängen: {0} | {1}".format(ecat.count(), lcat.count()))
            objs = objs.filter(
                Q(eventTemplate__eventCategory__in=ecat) | 
                Q(eventTemplate__eventLocation__categories__in=lcat) 
            )
            
        return objs.order_by('starttime')
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["body_id"] = "b_home"
        return context

def question(request, question_id):
    # return HttpResponse("Bämski Index.")
    if question_id is None or question_id < 0:
        question_id = 1
    question = get_object_or_404(Question, pk=question_id) 
    
    _pq = question.question.all().first().prevQuestion
    # print("PrevQUestion:", pq)
    if _pq is not None:
        pq = _pq.id
    else:
        pq = -1
    
    # user, users questionrun
    # lastquestion (every already saved answer is ignored)
    # last question answer
    if request.method == 'POST':
        if request.user.is_authenticated:
            user = request.user
            questionrun = user.currentQuestionRun

            # Get form data //TODO maybe build dynamic form und so
            # answers = dict(request.POST.lists())
            # print(answers)
            # just save the answer of prev question
            print("Got User and questionrun")
            if pq > 0:
                sel = request.POST.get('q{0}'.format(pq))
                print("PQ:{0}, PQS: {1}".format(pq, sel))
                
                pquestion = Question.objects.get(pk=pq)
                pselection = ChoiceOption.objects.get(pk=sel)
                # ans = UserSelection(user, pq, sel, questionRun=questionrun)
                # //TODO bestehende Antworten überschreiben oder sowas
                ans = UserSelection(user=user, question=pquestion, selection=pselection, questionRun=questionrun)
                print(ans)
                ans.save()
            else:
                print("No prev Q ")

        else:
            # do not save anything
            print("No user")
            pass
    else:
        print("No POST Method")
            
    context = {"body_id": "b_content", "question": question, "curquestionkey": "q{0}".format(question_id), "prevquestion":  pq} 
    return render(request, 'ooh/fragen.html', context=context)

def questionFinish(request):
    pass
# class Question(generic.DetailView):
#     template_name="ooh/fragen.html"
#     model = Question
#     context_object_name = "question"

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
                    # print(request.POST)
                    
                    # plz = form.cleaned_data['plz']
                    # cityname = form.cleaned_data['cityname']
                    plz = request.POST['plz']
                    cityname = request.POST['cityname']
                    location = Location.objects.get(plz=plz, cityname=cityname)
                    # print(location)
                    form.save()
                    # get User back to save location
                    us = OohUser.objects.get(email=form.cleaned_data['email'])
                    us.location = location
                    us.save()
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
    context_object_name = 'recommended_events'
    def get_queryset(self):
        # ev = Event.objects.get(name='Schnitzeltag')
        # print(ev.calculatedratings())
        # return EventLocation.objects.filter(locationID__plz=68159)
        return Event.objects.filter(Q(starttime__gte=datetime.date.today())).order_by('starttime')

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
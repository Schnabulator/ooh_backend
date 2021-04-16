from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views import generic
from django.template import Context
from .models import Location, EventLocation, Event, OohUser, Participate, Question, ChoiceOption, UserSelection, EventCategory, LocationCategory
from .forms import UserLoginForm, RegLoginSwitch, OohUserCreationForm, UserLocation
from django.contrib.auth import authenticate, login
from django.db.models import Q, Count, Sum


from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView #, RegisterView
from django.views.generic.edit import ProcessFormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import datetime

User = get_user_model()

class index(generic.ListView):
    model = Event
    template_name = 'ooh/index.html'
    context_object_name = 'recommended_events'
    def get_queryset(self):
        # //TODO filter from user has to be set here!
        # User filter
        if not self.request.user.is_authenticated:
            return None
        # Evaluation order needed!

        lcat = LocationCategory.objects.filter(
            choiceoption__userselection__user=self.request.user,
            choiceoption__userselection__questionRun=self.request.user.currentQuestionRun,
            choiceoption__userselection__valid=True,
            # choiceoption__question__firstQuestion=True
        ).order_by('choiceoption__question__priority_in_filtering').distinct()
        ecat = EventCategory.objects.filter(
            choiceoption__userselection__user=self.request.user,
            choiceoption__userselection__questionRun=self.request.user.currentQuestionRun,
            choiceoption__userselection__valid=True,
            # choiceoption__question__firstQuestion=True
        ).order_by('choiceoption__question__priority_in_filtering').distinct()
        print(lcat.exists(), "|", ecat.exists())
        for l in lcat:
            print("Location:", l)
        for e in ecat:
            print("Event:", e)

        
        
        events1 = Event.objects.filter(
            Q(starttime__gte=datetime.date.today()) &
            Q(eventTemplate__eventLocation__categories__in=lcat) |
            Q(starttime__gte=datetime.date.today()) &
            Q(eventTemplate__eventCategory__in=ecat)
        ).annotate(
            num_fitting_location_categories=Count('eventTemplate__eventLocation__categories')
        ).annotate(
            num_fitting_event_categories=Count('eventTemplate__eventCategory')
        ).order_by('-num_fitting_location_categories', '-num_fitting_event_categories', 'starttime').distinct()
        # ).order_by('num_fitting_location_categories').distinct()
        
        #//TODO seems like the order function does stupid stuff. I think Schnitzeltag has to be before shot friday
        print("Found {0} matching lcategories and {1} matching ecategories".format(
            events1[0].num_fitting_location_categories, events1[0].num_fitting_event_categories))
                
        # for ev in events1:
        #     # First print how many matching categories were found
        #     print("Event", ev.num_fitting_location_categories, " und ", ev.num_fitting_event_categories)
       
        return events1
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["body_id"] = "b_home"
        return context

# @userloginrequired
def questionFinish(request):
    # if request.method != "POST":
    #     pass #404 oder so
    # else:
    # if request.user.is_authenticated:
    #     request.user.questionRun = request.user.questionRun + 1
    #     request.user.save()
    context = {"body_id": "b_content"} 
    return render(request, 'ooh/questionend.html', context=context)

def question(request, question_id):
    # return HttpResponse("Bämski Index.")
    if question_id is None or question_id < 0:
        question_id = 1
    question = get_object_or_404(Question, pk=question_id) 
    choice = -1
    _pq = question.question.all().first().prevQuestion
    # print("PrevQUestion:", pq)
    if _pq is not None:
        pq = _pq.id
    else:
        pq = question_id
    if request.user.is_authenticated:
        user = request.user
        questionrun = user.currentQuestionRun
        print("Got User and questionrun")
        cquestion = Question.objects.get(pk=question_id)
        try:
            ans = UserSelection.objects.get(user=user, question=cquestion, questionRun=questionrun)
            choice = ans.selection.id
            print("Choice is", choice)
        except UserSelection.DoesNotExist:
            choice = -1
            print("Choice notfound ", choice)
    else:
        print("No user")
        pass
    if request.method == 'POST':
        # If currentquestion is the last one, save answer if provided
        if question.lastQuestion:
            sel = request.POST.get('q{0}'.format(question_id))
            if sel is not None and len(sel) > 0:
                print("Got selection for currentquestion")
                cselection = ChoiceOption.objects.get(pk=sel)
                try:
                    ans = UserSelection.objects.get(user=user, question=question, questionRun=questionrun)
                    ans.selection = cselection
                    ans.save()
                    print("Found Userselection and overwrite it")
                except UserSelection.DoesNotExist:
                    ans = UserSelection(user=user, question=question, selection=cselection, questionRun=questionrun)
                    ans.save()
                    print("Found no Userselection and created it")
                print(ans)
                ans.save()
        if pq > 0:
            sel = request.POST.get('q{0}'.format(pq))
            print("PQ:{0}, PQS: {1}".format(pq, sel))
            
            pquestion = Question.objects.get(pk=pq)
            pselection = ChoiceOption.objects.get(pk=sel)
            try:
                ans = UserSelection.objects.get(user=user, question=pquestion, questionRun=questionrun)
                ans.selection = pselection
                ans.save()
                print("Found Userselection and overwrite it")
            except UserSelection.DoesNotExist:
                ans = UserSelection(user=user, question=pquestion, selection=pselection, questionRun=questionrun)
                ans.save()
                print("Found no Userselection and created it")
            print(ans)
            ans.save()
        else:
            print("No prev Q ")
    else:
        print("No POST Method")
    # selection = UserSelection.objects.get(user=user, question=pquestion, questionRun=questionrun)
    context = {"body_id": "b_content", "question": question, "curquestionkey": "q{0}".format(question_id), "prevquestion":  pq, "checkeditem": choice} 
    return render(request, 'ooh/fragen.html', context=context)



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
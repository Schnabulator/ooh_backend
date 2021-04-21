from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views import generic
from django.template import Context
from .models import Location, EventLocation, Event, OohUser, Participate, Question, ChoiceOption, UserSelection, EventCategory, LocationCategory, EventTemplate
from .forms import UserLoginForm, RegLoginSwitch, OohUserCreationForm, UserLocation, AddEvent, ParticipateForm
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
        born = self.request.user.birthday
        today = datetime.date.today()
        age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        print("DATE: ", born, today, age)
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
        # print(lcat.exists(), "|", ecat.exists())
        
        events1 = Event.objects.filter(
            Q(starttime__gte=datetime.date.today()),
            Q(eventTemplate__mininumage__lte=age),
            Q(eventTemplate__eventLocation__categories__in=lcat) |
            Q(eventTemplate__eventCategory__in=ecat)
        ).annotate(
            num_fitting_location_categories=Count('eventTemplate__eventLocation__categories')
        ).annotate(
            num_fitting_event_categories=Count('eventTemplate__eventCategory')
        ).order_by('-num_fitting_location_categories', '-num_fitting_event_categories', 'starttime').distinct()
        # ).order_by('num_fitting_location_categories').distinct()
        
        #//TODO seems like the order function does stupid stuff. I think Schnitzeltag has to be before shot friday
        #print("Found {0} matching lcategories and {1} matching ecategories".format(events1[0].num_fitting_location_categories, events1[0].num_fitting_event_categories))
       
        return events1
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["body_id"] = "b_home"
        return context


def questionFinish(request):
    # if request.method != "POST":
    #     pass #404 oder so
    # else:
    # if request.user.is_authenticated:
    #     request.user.questionRun = request.user.questionRun + 1
    #     request.user.save()
    context = {"body_id": "b_content"} 
    return render(request, 'ooh/questionend.html', context=context)

@login_required(login_url="/profile/login")
def question(request, question_id):
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
                    plz = request.POST['plz']
                    cityname = request.POST['cityname']
                    try:
                        # cityname does not need to be exact match
                        location = Location.objects.get(plz=plz, cityname__icontains=cityname) 
                    except Location.DoesNotExist:
                        return JsonResponse({'error': 'Keinen Ort gefunden.', 'where': 'adress'})
                    except Location.MultipleObjectsReturned:
                        return JsonResponse({'error': 'Mehrere Ort gefunden.', 'where': 'adress'})
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
                    return JsonResponse({'error': 'Registrierung fehlerhaft.'}, status=400)
            elif form.cleaned_data['formular'] == "login":
                # Login handler
                form = UserLoginForm(request.POST)
                if form.is_valid():
                    print("Login")
                    user = form.cleaned_data['email']
                    pw = form.cleaned_data['password1']
                    user = authenticate(request,username=user,password=pw)
                    if user is not None:
                        login(request,user)
                        print("Successful logged in "+ user.email)
                        return JsonResponse({'success': 'Login war erfolgreich.'})
                    else:
                        print("User isnt authenticated")
                        return JsonResponse({'error': 'E-Mail oder Passwort falsch'}, status=404)
                else:
                    print(form.errors)
                    return JsonResponse({'error': 'Server Error'}, status=400)
            else:
                print("Not login and reg")
                return JsonResponse({'error': 'Server Error'}, status=501)
        else: 
            print("Form error loginreg")
            print(form.errors)
            return JsonResponse({'error': 'Server Error'}, status=500)

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
        # return Event.objects.all().order_by('starttime')
        return Event.objects.filter(Q(starttime__gte=datetime.date.today())).order_by('starttime')
    def get_context_data(self, **kwargs):
        context = super(EventView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            parti = Participate.objects.filter(user=self.request.user, event__in=self.object_list).values_list('event', flat=True)
            # print(parti)
            parti = list(parti)
            context.update({'participating': parti})
        return context


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

def impressum(request):
    template_name = 'ooh/impressum.html'
    context = {"body_id": "b_content"} 
    return render(request, template_name=template_name, context=context)

def newsletter(request):
    template_name = 'ooh/newsletter.html'
    context = {"body_id": "b_content"} 
    return render(request, template_name=template_name, context=context)

def add_event(request):
    if request.method == "POST":
        form = AddEvent(request.POST)
        print(form)
        err = {}
        if form.is_valid():
            try:
                # First get the location
                loc = Location.objects.get(
                   plz=form.cleaned_data['plz'],
                   cityname__icontains=form.cleaned_data['cityname'], 
                )
                if form.cleaned_data['room'] is not None and len(form.cleaned_data['room']) > 0:
                    (eloc, cr) = EventLocation.objects.get_or_create(
                        location=loc,
                        name=form.cleaned_data['locationName'], 
                        street__icontains=form.cleaned_data['street'], 
                        room__iexact=form.cleaned_data['room'],
                    )
                else:
                    (eloc, cr) = EventLocation.objects.get_or_create(
                        location=loc,
                        name=form.cleaned_data['locationName'], 
                        street__icontains=form.cleaned_data['street'], 
                    )
                if cr:
                    # New Eventlocation was added
                    pass
                else:
                    # Eventlocation was found
                    pass
                
                # Then create a Template if necessary
                try:

                    temp = EventTemplate.objects.get(
                        eventLocation=eloc,
                        name__iexact=form.cleaned_data['eventName'],
                    )
                except EventTemplate.DoesNotExist:
                    # Create
                    temp = EventTemplate(
                        name = form.cleaned_data['eventName'],
                        mininumage = form.cleaned_data['age'],
                        description = form.cleaned_data['description'],
                        eventLocation=eloc,
                        organizer=request.user,
                        pricecat=form.cleaned_data['pricecat'],
                        picture=form.cleaned_data['picture'],
                    )
                    temp.save()
                #  Finally add the Event itself
                event = Event(
                    eventTemplate=temp,
                    takeplace=1,
                    starttime=form.cleaned_data['starttime'],
                    endtime=form.cleaned_data['endtime'],
                    intervalInDays=form.cleaned_data['intervalInDays'],
                )
                print(
                    "EVENTADDER",
                    event.starttime, 
                    event.endtime, 
                    event.intervalInDays,
                    event.eventTemplate.name,
                    event.eventTemplate.eventLocation.name,
                    event.eventTemplate.eventLocation.location.cityname,
                )
                event.save()
            except Location.DoesNotExist:
                err['location'] = "unknown"
            except EventLocation.DoesNotExist:
                err['eventlocation'] = "unknown"
            except EventTemplate.DoesNotExist:
                err['eventtemplate'] = "unknown"
            except Event.DoesNotExist:
                err['event'] = "unknown"
        else:
            print("Unvalid formular\n", form.errors)
    else:
        form = AddEvent()
    return redirect('ooh:profile')

def autocomplete_event(request):
    pass

def participate_event(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = ParticipateForm(request.POST)
            if form.is_valid():
                try:
                    ev = Event.objects.get(pk=form.cleaned_data['eventID'])
                    prob = form.cleaned_data['probability'] 
                    if prob is None or prob <0 or prob >100:
                        prob=100
                    (parti, cr) = Participate.objects.get_or_create(user=request.user, event=ev, probability=prob)
                    if cr:
                        # redirect to event page
                        return JsonResponse({'success': 'Erfolgreich teilgenommen.'})
                    else:
                        # redirect to event page

                        return JsonResponse({'success': 'Bereits teilgenommen.'})
                except Event.DoesNotExist:
                    return JsonResponse({'error': 'Dieses Event gibt es nicht'}, status=404)
                
        else:
            # User has to be authenticated
            return JsonResponse({'error': 'Bitte anmelden'}, status=401)
    else:
        # Everything else is forbidden
        return JsonResponse({'error': 'Das darfst du nicht'}, status=405)
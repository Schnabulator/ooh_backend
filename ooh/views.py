from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views import generic
from django.template import Context
from .models import Location, EventLocation, Event, OohUser, Participate, Question, ChoiceOption, UserSelection, EventCategory, LocationCategory, EventTemplate
from .forms import UserLoginForm, RegLoginSwitch, OohUserCreationForm, UserLocation, AddEvent, ParticipateForm, ChangeUser, ResetUserPreferences
from django.contrib.auth import authenticate, login
from django.db.models import Q, Count, Sum


from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView #, RegisterView
from django.views.generic.edit import ProcessFormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import datetime

User = get_user_model()
# questionend  return values
########## Club ##########
# club_gehoben_elektro = "Disco Fox"
# club_gehoben_rock = "Heavy Metal Poger"
# club_gehoben_pop = "Hit Friday Follower"
# club_gehoben_hiphop = "Gangsta Rapper"

# club_preiswert_elektro = "Raver*in"
# club_preiswert_rock = "Garage Rocker*in"
# club_preiswert_pop = "Spotify Groover*in"
# club_preiswert_hipHop = "Old Schooler*in"

########## Bars ##########
# bar_gehoben_elektro = "House Dancer*in"
# bar_gehoben_rock = "Classic Rocker*in"
# bar_gehoben_pop = "Jackson Verehrer*in"
# bar_gehoben_hipHop = "HipHop Fanatiker*in"

# bar_preiswert_elektro = "Ambient Chiller"
# bar_preiswert_rock = "Softrocker*in"
# bar_preiswert_pop = "Jazzer"
# bar_preiswert_hiphop = "Battle Rapper"

########## Essen ##########
# essen_gehoben_amerikanisch = "Steak Genießer*in"
# essen_gehoben_europa =  "Pasta Genussmensch"
# essen_gehoben_asia =  "Sushi Guru"
# essen_gehoben_afrikanisch =  "Couscous Feinschmecker"

# essen_preiswert_amerikanische = "Burger Schlinger*in"
# essen_preiswert_europa = "Pizza Verdrücker"
# essen_preiswert_asia = "Nudelboxsuchti "
# essen_preiswert_afrikanisch = "Fallafel Nascher"

########## Kultur ##########
# kulturelles_vorführungen = "Unterhaltungsfetischist"
# kulturelles_ausstellungen = "Kunstliebhaber"

# quenstionend return values end
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
        # print("DATE: ", born, today, age)
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
        # print(ecat, "\n", lcat)
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
        # print(events1)
        #//TODO seems like the order function does stupid stuff. I think Schnitzeltag has to be before shot friday
        #print("Found {0} matching lcategories and {1} matching ecategories".format(events1[0].num_fitting_location_categories, events1[0].num_fitting_event_categories))
       
        return events1
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["body_id"] = "b_home"
        return context

@login_required(login_url="/profile/login")
def questionFinish(request):
    # first save the last answer
    # print(request.POST)
    please_wait_hint = False
    for key, value in request.POST.items():
        if key.startswith("q"):
            question_id = key[1:]
            question = get_object_or_404(Question, pk=question_id)
            if value is not None and len(value) > 0:
                cselection = ChoiceOption.objects.get(pk=value)
                try:
                    ans = UserSelection.objects.get(user=request.user, question=question, questionRun=request.user.currentQuestionRun)
                    ans.selection = cselection
                    ans.save()
                    # print("Found Userselection and overwrite it")
                except UserSelection.DoesNotExist:
                    ans = UserSelection(user=request.user, question=question, selection=cselection, questionRun=request.user.currentQuestionRun)
                    ans.save()
                    # print("Found no Userselection and created it")
                break

    # Get result
    allanswers = UserSelection.objects.filter(
        user=request.user,
        questionRun=request.user.currentQuestionRun,
        valid=1,
    )
    # print(allanswers)
    ans =  []
    for a in allanswers:
        ans.append(a.selection.text.lower())
    # print("nommel\n", ans)
    
    result = ""
    #//TODO wenn die damit glücklich sind kann man die kacke auch noch bisschen zusammenfassen und kürzen
    # club
    if 'club' in ans:
      #  print("# club")
        if 'gehoben' in ans:
          #  print("# gehoben")
            # result = "gehobenen "
            # Music
            if 'pop' in ans:
              #  print("# pop")
                result = result + "Hit Friday Follower"
            elif 'rock' in ans:
              #  print("# rock")
                result = result + "Heavy Metal Poger"
            elif 'hip-hop' in ans:
              #  print("# hip-hop")
                result = result + "Gangster Rapper"
            elif 'techno' in ans or 'electro' in ans or 'elektro' in ans:
              #  print("# techno")
                result = result + "Disco Fox"
        elif 'preiswert' in ans:
          #  print("# billig")
            # result = "preiswerten "
            # Music
            if 'pop' in ans:
              #  print("# pop")
                result = result + "Spotify Groover*in"
            elif 'rock' in ans:
              #  print("# rock")
                result = result + "Garage Rocker*in"
            elif 'hip-hop' in ans:
              #  print("# hip-hop")
                result = result + "Old Schooler*in"
            elif 'techno' in ans or 'electro' in ans or 'elektro' in ans:
              #  print("# techno")
                result = result + "Raver*in"

    elif 'bar' in ans:
      #  print("# bar")
        if 'gehoben' in ans:
          #  print("# gehoben")#
            # result = "gehobenen "
            # Music
            if 'pop' in ans:
              #  print("# pop")
                result = result + "Jackson Verehrer*in"
            elif 'rock' in ans:
              #  print("# rock")
                result = result + "Classic Rocker*in"
            elif 'hip-hop' in ans:
              #  print("# hip-hop")
                result = result + "HipHop Fanatiker*in"
            elif 'techno' in ans:
              #  print("# techno")
                result = result + "House Dancer*in"
        elif 'preiswert' in ans:
          #  print("# billig")
            # result = "preiswerten "
            # Music
            if 'pop' in ans:
              #  print("# pop")
                result = result + "Jazzer"
            elif 'rock' in ans:
              #  print("# rock")
                result = result + "Softrocker*in"
            elif 'hip-hop' in ans:
              #  print("# hip-hop")
                result = result + "Battle Rapper"
            elif 'techno' in ans:
              #  print("# techno")
                result = result + "Ambient Chiller"
    elif 'essen' in ans:
        # Food Stuff
        if 'gehoben' in ans:
            if 'amerikanisch' in ans:
                result = result + "Steak Genießer*in"
            if 'europäisch' in ans:
                result = result + "Pasta Genussmensch"
            if 'asiatisch' in ans:
                result = result + "Sushi Guru"
            if 'afrikanisch' in ans:
                result = result + "Couscous Feinschmecker"
        if 'preiswert' in ans:
            if 'amerikanisch' in ans:
                result = result + "Burger Schlinger*in"
            if 'europäisch' in ans:
                result = result + "Pizza Verdrücker"
            if 'asiatisch' in ans:
                result = result + "Nudelboxsuchti"
            if 'afrikanisch' in ans:
                result = result + "Fallafel Nascher*in"
    elif 'ausstellungen (museum, gallerie)' in ans:
        result = result + "Kunstliebhaber"
        please_wait_hint = True
    elif 'vorstellungen (theater, oper, kino)' in ans:
        result = result + "Unterhaltungsfetischist"
        please_wait_hint = True

    # result = "Arsch"
    context = {"body_id": "b_content", "result": result, "please_wait": please_wait_hint} 
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
            if sel is not None:
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
    return render(request, 'ooh/question.html', context=context)



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
    template_name = 'ooh/eventview.html'
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
        please_wait_hint = False
        # Get result
        allanswers = UserSelection.objects.filter(
            user=request.user,
            questionRun=request.user.currentQuestionRun,
            valid=1,
        )
        # print(allanswers)
        
        ans =  []
        for a in allanswers:
            ans.append(a.selection.text.lower())
        # print("nommel\n", ans)
        
        result = ""
        #//TODO wenn die damit glücklich sind kann man die kacke auch noch bisschen zusammenfassen und kürzen
        # club
        if 'club' in ans:
        #  print("# club")
            if 'gehoben' in ans:
            #  print("# gehoben")
                # result = "gehobenen "
                # Music
                if 'pop' in ans:
                #  print("# pop")
                    result = result + "Hit Friday Follower"
                elif 'rock' in ans:
                #  print("# rock")
                    result = result + "Heavy Metal Poger"
                elif 'hip-hop' in ans:
                #  print("# hip-hop")
                    result = result + "Gangster Rapper"
                elif 'techno' in ans or 'electro' in ans or 'elektro' in ans:
                #  print("# techno")
                    result = result + "Disco Fox"
            elif 'preiswert' in ans:
            #  print("# billig")
                # result = "preiswerten "
                # Music
                if 'pop' in ans:
                #  print("# pop")
                    result = result + "Spotify Groover*in"
                elif 'rock' in ans:
                #  print("# rock")
                    result = result + "Garage Rocker*in"
                elif 'hip-hop' in ans:
                #  print("# hip-hop")
                    result = result + "Old Schooler*in"
                elif 'techno' in ans or 'electro' in ans or 'elektro' in ans:
                #  print("# techno")
                    result = result + "Raver*in"

        elif 'bar' in ans:
        #  print("# bar")
            if 'gehoben' in ans:
            #  print("# gehoben")#
                # result = "gehobenen "
                # Music
                if 'pop' in ans:
                #  print("# pop")
                    result = result + "Jackson Verehrer*in"
                elif 'rock' in ans:
                #  print("# rock")
                    result = result + "Classic Rocker*in"
                elif 'hip-hop' in ans:
                #  print("# hip-hop")
                    result = result + "HipHop Fanatiker*in"
                elif 'techno' in ans:
                #  print("# techno")
                    result = result + "House Dancer*in"
            elif 'preiswert' in ans:
            #  print("# billig")
                # result = "preiswerten "
                # Music
                if 'pop' in ans:
                #  print("# pop")
                    result = result + "Jazzer"
                elif 'rock' in ans:
                #  print("# rock")
                    result = result + "Softrocker*in"
                elif 'hip-hop' in ans:
                #  print("# hip-hop")
                    result = result + "Battle Rapper"
                elif 'techno' in ans:
                #  print("# techno")
                    result = result + "Ambient Chiller"
        elif 'essen' in ans:
            # Food Stuff
            if 'gehoben' in ans:
                if 'amerikanisch' in ans:
                    result = result + "Steak Genießer*in"
                if 'europäisch' in ans:
                    result = result + "Pasta Genussmensch"
                if 'asiatisch' in ans:
                    result = result + "Sushi Guru"
                if 'afrikanisch' in ans:
                    result = result + "Couscous Feinschmecker"
            if 'preiswert' in ans:
                if 'amerikanisch' in ans:
                    result = result + "Burger Schlinger*in"
                if 'europäisch' in ans:
                    result = result + "Pizza Verdrücker"
                if 'asiatisch' in ans:
                    result = result + "Nudelboxsuchti"
                if 'afrikanisch' in ans:
                    result = result + "Fallafel Nascher*in"
        elif 'ausstellungen (museum, gallerie)' in ans:
            result = result + "Kunstliebhaber"
            please_wait_hint = True
        elif 'vorstellungen (theater, oper, kino)' in ans:
            result = result + "Unterhaltungsfetischist"
            please_wait_hint = True

    
        
    
        context = {"body_id": "b_content", "result": result, "please_wait": please_wait_hint} 
        return render(self.request, template_name=self.template_name, context=context)

    @method_decorator(login_required(login_url="/profile/login"))
    def post(self, request, *args, **kwargs):
        form = ChangeUser(request.POST)
        us = request.user
        if form.is_valid():
            print("Valid Form for change of user "+request.user.email)
            plz = form.cleaned_data['plz']
            cityname = form.cleaned_data['cityname']
            street = form.cleaned_data['street']
            housenumber = form.cleaned_data['housenumber']
            firstname = form.cleaned_data['firstname']
            lastname = form.cleaned_data['lastname']
            birthday = form.cleaned_data['birthday']
            
            if firstname is not None and len(firstname) > 1:
                us.firstname = firstname
            if lastname is not None and len(lastname) > 1:
                us.lastname = lastname
            if birthday is not None:
                us.birthday = birthday
            if street is not None and len(street) > 1:
                us.street = street
            if housenumber is not None and len(housenumber) >= 1:
                us.housenumber = housenumber
            if plz is not None and cityname is not None and len(plz)>=4 and len(cityname) >= 2:
                location = Location.objects.get(plz=plz, cityname=cityname)
                if location is None:
                    # //TODO Make a error message in se formular
                    context = {"body_id": "b_content"} 
                    return render(self.request, template_name=self.template_name, context=context)
                us.location = location
            us.save()
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

#  //TODO eventlocation kategorien müssen gesetzt werden 
def add_event(request):
    if request.method == "POST":
        form = AddEvent(request.POST, request.FILES)
        # print(form)
        err = {}
        if form.is_valid():
            try:
                # First get the location
                loc = Location.objects.get(
                   plz=form.cleaned_data['plz'],
                   cityname__icontains=form.cleaned_data['cityname'], 
                )

                #  Smoking has to be set at the location itself
                smok = form.cleaned_data['smoking']
                _scat = LocationCategory.objects.filter(filter_name=smok)
                if _scat.exists():
                    scat = _scat.first()
                else:
                    if smok == "nosmoking":
                        name="Keinen"
                    elif smok == "innersmoking":
                        name="Innen"
                    elif smok == "outersmoking":
                        name="Außen"
                    scat = LocationCategory.objects.create(
                        filter_name=smok,
                        name=name,
                    )
                # Location type
                ltype = form.cleaned_data['locationType']
                _scat = LocationCategory.objects.filter(filter_name=ltype)
                if _scat.exists():
                    lcat = _scat.first()
                else:
                    lcat = LocationCategory.objects.create(
                        filter_name=smok.lower(),
                        name=name,
                    )
                
                if form.cleaned_data['room'] is not None and len(form.cleaned_data['room']) > 0:
                    try:
                        eloc = EventLocation.objects.get(
                            location=loc,
                            name=form.cleaned_data['locationName'], 
                            street__icontains=form.cleaned_data['street'], 
                            room__iexact=form.cleaned_data['room'],
                        )
                        # Do not override Categories! or add them 🤔 :thinkingface:
                    except EventLocation.DoesNotExist:
                        eloc = EventLocation.objects.create(
                            location=loc,
                            name=form.cleaned_data['locationName'], 
                            street=form.cleaned_data['street'], 
                            room=form.cleaned_data['room'],
                        )
                        eloc.categories.add(lcat)
                        eloc.categories.add(scat)
                        eloc.save()
                        print("Added Eventlocation")
                else:
                    try:
                        eloc = EventLocation.objects.get(
                            location=loc,
                            name=form.cleaned_data['locationName'], 
                            street__icontains=form.cleaned_data['street'], 
                        )
                    except EventLocation.DoesNotExist:
                        eloc = EventLocation.objects.create(
                            location=loc,
                            name=form.cleaned_data['locationName'], 
                            street=form.cleaned_data['street'], 
                        )
                        eloc.categories.add(lcat)
                        eloc.categories.add(scat)
                        eloc.save()
                        print("Added Eventlocation")
                
                
                # Food and Music is Eventcategory
                special = form.cleaned_data['specialcategory']
                restaurant = True if form.cleaned_data['locationType'].lower()=="restaurant" else False
                _scat = EventCategory.objects.filter(
                        Q(filter_name__iexact=special) |
                        Q(name__iexact=special)
                )
                if _scat.exists():
                    spcat = _scat.first()
                else:
                    spcat = EventCategory.objects.create(
                        filter_name=special,
                        name=special,
                    )

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
                        picture=request.FILES['picture'],
                    )
                    temp.save()
                    print("Added Template")
                # Add event categories
                temp.eventCategory.add(spcat)
                for cat in form.cleaned_data['categories'].split(','):
                    cat = cat.strip()
                    c = EventCategory.objects.filter(
                        Q(name__icontains=cat) |
                        Q(filter_name__icontains=cat)
                    )
                    if not c.exists():
                        c = EventCategory.objects.create(
                            name=cat,
                            filter_name=cat.lower(),
                        )
                    else: 
                        c = c.first()
                    # if EventCategory.eventTemplate_set.filter(eventCategory=c):
                    temp.eventCategory.add(c)

                #  Finally add the Event itself
                event = Event(
                    eventTemplate=temp,
                    takeplace=1,
                    starttime=form.cleaned_data['starttime'],
                    endtime=form.cleaned_data['endtime'],
                    intervalInDays=form.cleaned_data['intervalInDays'],
                    until=form.cleaned_data['until'],
                )

                # print(
                #     "EVENTADDER\n",
                #     event.starttime, 
                #     event.endtime, 
                #     event.intervalInDays,
                #     event.until,
                #     "\nEventtemplate shit\n",
                #     event.eventTemplate.name,
                #     event.eventTemplate.eventLocation.name,
                #     event.eventTemplate.eventLocation.location.cityname,
                # )
                event.save()
                print("Added event")
            except Location.DoesNotExist:
                err['location'] = "unknown"
            except EventTemplate.DoesNotExist:
                err['eventtemplate'] = "unknown"
            except Event.DoesNotExist:
                err['event'] = "unknown"
        else:
            # print("Unvalid formular\n", form.errors)
            pass
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
                    if prob is None or prob <0 or prob > 100:
                        prob = 100
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

@login_required(login_url="/profile/login")
def reset_user_preferences(request):
    # first check if valid
    if request.method =="POST":
        form = ResetUserPreferences(request.POST)
        if form.is_valid():
            if form.cleaned_data['submitdelete'] == 'yes':
                # then delete
                user = request.user
                qr = user.currentQuestionRun
                UserSelection.objects.filter(user=user, questionRun=qr).delete()
    return redirect('/profile/')
    




# questionend start begin stuff blabla hihi
# return None
#     fq = Question.objects.get(firstQuestion=1)
#     loc = allanswers.get(question=fq)

#     # now build the result

#     # Location
#     if "kultur" in loc.selection.text.lower():
#       #  print("# Kultur")
#         # no price, just different between vorführung und ausstellung
#     else:
#         pq = Question.objects.filter(name__icontains="preisklasse")
#         print("PQ", pq)
#         price = allanswers.get(question__in=pq)
#         sq = Question.objects.filter(name__icontains="raucher")
#         print("SQ", sq)
#         smok = allanswers.get(question__in=sq)

#         if "feiern" in loc.selection.text.lower():
#             if "nicht" in smok.selection.text.lower():
#               #  print("# nicht raucher")
#                 result = "nichtrauchende/r "
#             else: 
#               #  print("# raucher")
#                 result = "rauchende/r "

#           #  print("# feiern")
#             bcq = Question.objects.get(name__icontains="liebsten feier")
#             barclub = allanswers.get(question=bcq)
#             if "club" in barclub.selection.text.lower():
#               #  print("# club")
#                 if "preiswert" in price.selection.text.lower():
#                   #  print("# preiswert")
#                     result = result + ""
#                 else:
#                   #  print("# gehoben")
#             else:
#               #  print("# noclub / bar")
#                 if "preiswert" in price.selection.text.lower():
#                   #  print("# preiswert")
#                 else:
#                   #  print("# gehoben")
#         elif "essen" in loc.selection.text.lower():
#           #  print("# bar")
#             kq = Question.objects.get(name__icontains="küche")
#             kitchen = allanswers.get(question=kq)
#             if "amerika" in kitchen.selection.text.lower():

#                 if "preiswert" in price.selection.text.lower():
#                   #  print("# preiswert")
#                 else:
#                   #  print("# gehoben")
#             if "asiat" in kitchen.selection.text.lower():
#                 if "preiswert" in price.selection.text.lower():
#                   #  print("# preiswert")
#                 else:
#                   #  print("# gehoben")
#             if "europ" in kitchen.selection.text.lower():
#                 if "preiswert" in price.selection.text.lower():
#                   #  print("# preiswert")
#                 else:
#                   #  print("# gehoben")
#             if "afrika" in kitchen.selection.text.lower():
#                 if "preiswert" in price.selection.text.lower():
#                   #  print("# preiswert")
#                 else:
#                   #  print("# gehoben")
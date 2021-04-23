from django.db import models
import datetime
from datetime import date
from django.utils import timezone
from django.views import generic
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
# required for User referencing
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from .managers import OohUserManager


class Location(models.Model):
    cityname = models.CharField(max_length=255)
    plz = models.CharField(max_length=10)
    bundesland = models.CharField(max_length=50)
    def __str__(self):
        return str(self.plz) +" "+ self.cityname

class LocationCategory(models.Model):
    name = models.CharField(max_length=100)
    filter_name = models.CharField(max_length=100, blank=True, null=True)
    overcategory = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.filter_name:
            self.filter_name = self.name.lower()
        super(LocationCategory, self).save(*args, **kwargs)
    def filterName(self, *args, **kwargs):
        if self.filter_name:
            return self.filter_name 
        else: 
            return self.name.lower()

class EventCategory(models.Model):
    name = models.CharField(max_length=100)
    filter_name = models.CharField(max_length=100, blank=True, null=True)
    overcategory = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.filter_name:
            self.filter_name = self.name.lower()
        super(EventCategory, self).save(*args, **kwargs)
    def filterName(self, *args, **kwargs):
        if self.filter_name:
            return self.filter_name 
        else: 
            return self.name.lower()

class EventLocation(models.Model):
    name	= models.CharField(max_length=100)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    street	= models.CharField(max_length=50)
    # housenumber = models.CharField(max_length=10, blank=True)
    room	= models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    categories = models.ManyToManyField(LocationCategory)
    picture = models.ImageField(blank=True, null=True, upload_to='locations/%Y/%m')
    pricecat = models.IntegerField(default=0) # the higher the more expensive (0=nonrated)
    
    def getCategories(self):
        ret = ""
        qs = self.categories.all()
        for c in qs:
            ret += c.__str__().lower().replace(' ', '-') + " "
        return ret

    # //TODO periodically running functions to calculate rating
    def calculatedratings(self):
        # return [3,1]
        rat = EventLocationRating.objects.get(eventlocationID=self.locationID.id)
        if len(rat) == 0:
            # print("No Ratings available")
            return [0, 0]
        summedrating = 0
        for rating in rat:
            summedrating += rating.rating
        # print("Average rating: "+str(summedrating))
        return [summedrating/len(rat), len(rat)]
    def sameplz(self, plz):
        print("Called near method")
        return self.locationID__plz == plz
    def __str__(self):
        return self.name #+ " [%s]".format(self.locationID__name)
        
# Authentication shit
class OohUser(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = "email"
    EMAIL_FIELD    = "email"
    email    = models.EmailField(_('email address'), unique=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    birthday = models.DateField(null=True)
    currentQuestionRun = models.IntegerField(default=1)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(default=timezone.now)
    date_joined = models.DateTimeField(default=timezone.now)
    # //TODO coordinates for calculating distance
    street = models.CharField(max_length=50, blank=True)
    housenumber = models.CharField(max_length=10, blank=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, blank=True, null=True)    
    admin = models.BooleanField(default=False)
    defaultEventLocation = models.ForeignKey(EventLocation, on_delete=models.SET_NULL, blank=True, null=True, default=None)

    objects = OohUserManager()

class EventTemplate(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    cost = models.IntegerField(default=0)
    mininumage = models.PositiveSmallIntegerField(default=0)
    eventCategory = models.ManyToManyField(EventCategory)
    eventLocation = models.ForeignKey(EventLocation, on_delete=models.CASCADE)
    organizer = models.ForeignKey(OohUser, on_delete=models.CASCADE)
    pricecat = models.IntegerField(default=0) # the higher the more expensive (0=nonrated)
    picture = models.ImageField(blank=True, null=True, upload_to='events/%Y/%m')
    # //TODO periodically running functions to calculate rating
    def __str__(self):
        return self.name + " @{0}".format(self.eventLocation)
    def getCategories(self):
        ret = ""
        qs = self.eventCategory.all()
        for c in qs:
            ret += c.__str__().lower().replace(' ', '-') + " "
        # preisklasse
        if self.pricecat > 0:
            if self.pricecat == 1:
                return "preiswert"
            else:
                return "gehoben"
        else:
            if self.eventLocation.pricecat == 1:
                return "preiswert"
            else:
                return "gehoben"
        return ret

    def calculatedratings(self):
        rat = EventRating.objects.filter(eventTemplate=self.id)
        if len(rat) == 0:
            # print("No Ratings available")
            return [0, 0]
        summedrating = 0
        for rating in rat:
            summedrating += rating.rating
        # print("Average rating: "+str(summedrating))
        return [(summedrating/len(rat)), len(rat)]

class Event(models.Model):
    eventTemplate = models.ForeignKey(EventTemplate, on_delete=models.CASCADE, null=True, blank=True)
    takeplace = models.BooleanField(default=True)
    promoted = models.BooleanField(default=False)
    starttime = models.DateTimeField()
    endtime = models.DateTimeField()
    # intervalOffset = models.CharField(max_length=3, blank=True, null=True) # to seperate between weekly, monthly, ... events
    intervalInDays = models.IntegerField(blank=True, null=True) # after how many days should the next event be generated
    until = models.DateField(blank=True, null=True)
    def __str__(self):
        return self.eventTemplate.__str__() + " [{0}]".format(self.starttime)
    def timecheck(self):
        # //TODO evtl checken ob das auch über Zeitzonen hinweg funzt
        todaysDate = date.today() # + datetime.timedelta(days=1) #Wenn heute Freitag ist, stimmt Sonntag nicht
        eventDate = self.starttime.date()
        if todaysDate == eventDate:
            return "today"
        elif eventDate == todaysDate + datetime.timedelta(days=1):
            return "tomorrow"
        weekday = todaysDate.isoweekday()
        if weekday in (0,1,2,3): # Monday to Thursday
            # add (4-weekday)
            fridayoffset = 4 - weekday
            sundayoffset = 7 - weekday
            if eventDate >= todaysDate + datetime.timedelta(days=fridayoffset) and eventDate <= todaysDate + datetime.timedelta(days=sundayoffset):
                return "nextweekend"
        else: # if today is between friday and sunday, check if it nextweek (+7)
            fridayoffset = 2 - weekday  # 7 - weekday + 5
            sundayoffset = weekday      # 7 - weekday + 7
            if eventDate >= todaysDate + datetime.timedelta(days=fridayoffset) and eventDate <= todaysDate + datetime.timedelta(days=sundayoffset):
                return "nextweekend"
    def save(self, *args, **kwargs):
        this_time = self.starttime
        this_time2 = self.endtime
        if self.until is not None: #and self.until > self.starttime.date():
            print("Create event until ", self.until)
            while this_time.date() <= self.until:
                new_ev = Event(
                    eventTemplate = self.eventTemplate,
                    takeplace = self.takeplace,
                    promoted = self.promoted,
                    starttime = this_time,
                    endtime = this_time2,
                )
                # print("save", self.eventTemplate.name, this_time)
                super(Event, new_ev).save(*args, **kwargs)
                this_time = this_time + datetime.timedelta(self.intervalInDays)
                this_time2 = this_time2 + datetime.timedelta(self.intervalInDays)
        else:
            print("No valid until provided")
            super(Event, self).save(*args, **kwargs)
class Participate(models.Model):
    user = models.ForeignKey(OohUser, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    probability = models.PositiveSmallIntegerField()
    def __str__(self):
        return "{2} {0} [{1}]".format(self.event.eventTemplate.name, self.probability, self.user.email)

class EventRating(models.Model):
    rating = models.PositiveSmallIntegerField()
    description = models.TextField()
    user = models.ForeignKey(OohUser, on_delete=models.SET_NULL, null=True)
    eventTemplate = models.ForeignKey(EventTemplate, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    def __str__(self):
        return "{0}@{1} | {2}".format(self.eventTemplate.name, self.eventTemplate.eventLocation.name, self.user.email) # , self.description[:75] + (self.description[75:] and '..'))

class EventLocationRating(models.Model):
    rating = models.PositiveSmallIntegerField()
    description = models.TextField()
    user = models.ForeignKey(OohUser, on_delete=models.SET_NULL, null=True)
    eventlocation = models.ForeignKey(EventLocation, on_delete=models.CASCADE)
    def __str__(self):
        return "{0} | {1}".format(self.eventlocationID.name, self.user.email) #, self.description[:75] + (self.description[75:] and '..'))

class Question(models.Model):
    name = models.CharField(max_length=100)
    firstQuestion = models.BooleanField(default=False)
    lastQuestion = models.BooleanField(default=False)
    priority_in_filtering = models.IntegerField(default=1000)
    # prevQuestion = models.ForeignKey('self', on_delete=models.CASCADE, related_name='prevQuestion', blank=True, null=True)
    objects = models.Manager()
    def __str__(self):
        return str(self.pk)+" | "+ self.name

class ChoiceOption(models.Model):
    text = models.CharField(max_length=100)
    class_names = models.CharField(max_length=100, blank=True, null=True)
    filter_name = models.CharField(max_length=100, blank=True, null=True)
    nextQuestion = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='nextQuestion', blank=True, null=True)
    prevQuestion = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='prevQuestion', blank=True, null=True)
    result = models.CharField(max_length=100, blank=True, null=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='question')
    related_event_category = models.ManyToManyField(EventCategory, blank=True)
    related_location_category = models.ManyToManyField(LocationCategory, blank=True)
    def __str__(self):
        return self.text
    def save(self, *args, **kwargs):
        if not self.filter_name:
            self.filter_name = self.text.lower()
        super(ChoiceOption, self).save(*args, **kwargs)
    def filterName(self, *args, **kwargs):
        if self.filter_name:
            return self.filter_name 
        else: 
            return self.text.lower()

class UserSelection(models.Model):
    user = models.ForeignKey(OohUser, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selection = models.ForeignKey(ChoiceOption, on_delete=models.CASCADE)
    valid = models.BooleanField(default=True)
    questionRun = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now=True)
    def __str__(self):
        return "{0}[{1}]: {2} - {3}".format(self.user, self.questionRun, self.question, self.selection)

from django.db import models
import datetime
from django.utils import timezone
from django.views import generic
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
# required for User referencing
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from .managers import OohUserManager


class Location(models.Model):
    # locationID = models.AutoField() # auto increment integer key
    cityname = models.CharField(max_length=255)
    plz = models.CharField(max_length=10)
    bundesland = models.CharField(max_length=50)
    def __str__(self):
        return str(self.plz) +" "+ self.cityname

class EventLocation(models.Model):
    # eventLocationID =  models.AutoField()
    street	= models.CharField(max_length=50)
    housenumber = models.CharField(max_length=10, blank=True)
    # //TODO coordinates = 
    name	= models.CharField(max_length=100)
    room	= models.CharField(max_length=100, blank=True)
    locationID = models.ForeignKey(Location, on_delete=models.PROTECT)
    # //TODO picture = models.FileField 
    # //TODO periodically running functions to calculate rating
    #  //TODO tut nicht
    def calculatedratings(self):
        return [3,1]
        rat = EventLocationRating.objects.get(eventlocationID=self.locationID)
        
        if len(rat) == 0:
            print("No Ratings available")
            return [0, 0]
        summedrating = 0
        for rating in rat:
            summedrating += rating.rating
        print("Average rating: "+str(summedrating))
        return [summedrating/len(rat), len(rat)]
        pass
    def sameplz(self, plz):
        print("Called near method")
        return self.locationID__plz == plz
    def __str__(self):
        return self.name #+ " [%s]".format(self.locationID__name)
        
        # l = Location.objects.all()
        # print(self.location_set.all())
        
# Authentication shit
class OohUser(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = "email"
    EMAIL_FIELD    = "email"
    email    = models.EmailField(_('email address'),unique=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    birthday = models.DateField(null=True)
    
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

class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Event(models.Model):
    # eventID = models.AutoField()
    name = models.TextField()
    description = models.TextField()
    organizer = models.ForeignKey(OohUser, on_delete=models.CASCADE)
    location = models.ForeignKey(EventLocation, on_delete=models.CASCADE)
    takeplace = models.BooleanField(default=True)
    cost = models.IntegerField(default=0)
    promoted = models.BooleanField(default=False)
    starttime = models.DateTimeField()
    endtime = models.DateTimeField()
    mininumage = models.PositiveSmallIntegerField()
    category = models.ManyToManyField(Category)
    # //TODO periodically running functions to calculate reting
    def __str__(self):
        return self.name + " [{0}]".format(self.location)



class Participate(models.Model):
    customerID = models.ForeignKey(OohUser, on_delete=models.CASCADE)
    eventID = models.ForeignKey(Event, on_delete=models.CASCADE)
    probability = models.PositiveSmallIntegerField()
    def __str__(self):
        return "{0}_{1}".format(self.eventID__name, self.probability)

class EventRating(models.Model):
    # ratingID = models.AutoField()
    rating = models.PositiveSmallIntegerField()
    description = models.TextField()
    user = models.ForeignKey(OohUser, on_delete=models.SET_NULL, null=True)
    eventID = models.ForeignKey(Event, on_delete=models.CASCADE)
    def __str__(self):
        return "{0}_{1}-{2}: {3}".format(self.eventID__name, self.customerID__userID__email, self.description[:75] + (self.description[75:] and '..'))

class EventLocationRating(models.Model):
    # ratingID = models.AutoField()
    rating = models.PositiveSmallIntegerField()
    description = models.TextField()
    user = models.ForeignKey(OohUser, on_delete=models.SET_NULL, null=True)
    eventlocationID = models.ForeignKey(EventLocation, on_delete=models.CASCADE)
    def __str__(self):
        return "{0}_{1}-{2}: {3}".format(self.eventlocationID__name, self.customerID__userID__email, self.description[:75] + (self.description[75:] and '..'))


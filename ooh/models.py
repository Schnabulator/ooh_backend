from django.db import models
import datetime
from django.utils import timezone
from django.views import generic
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
# required for User referencing
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from .managers import OohUserManager



# Authentication shit
class OohUser(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = "email"
    EMAIL_FIELD    = "email"
    email    = models.EmailField(_('email address'),unique=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    birthday = models.DateField(null=True)
    REQUIRED_FIELDS = ['firstname', 'lastname', 'birthday',]
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(default=timezone.now)
    date_joined = models.DateTimeField(default=timezone.now)
    objects = OohUserManager()



# Create your models here.

class Location(models.Model):
    # locationID = models.AutoField() # auto increment integer key
    cityname = models.CharField(max_length=255)
    plz = models.CharField(max_length=10)
    bundesland = models.CharField(max_length=50)
    def __str__(self):
        return str(self.plz) +" "+ self.name

class EventLocation(models.Model):
    # eventLocationID =  models.AutoField()
    street	= models.CharField(max_length=50)	
    name	= models.CharField(max_length=100)
    room	= models.CharField(max_length=100, blank=True)
    locationID = models.ForeignKey(Location, on_delete=models.PROTECT)
    def sameplz(self, plz):
        print("Called near method")
        return self.locationID__plz == plz
    def __str__(self):
        return self.name #+ " [%s]".format(self.locationID__name)
        
        # l = Location.objects.all()
        # print(self.location_set.all())
        

class Customer(models.Model):
    admin = models.BooleanField(default=False)
    # alternativ get_user_model()
    userID = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    def __str__(self):
        return "[admin-{0}] {1}".format(self.admin, self.userID__email)

class Organizer(models.Model):
    location = models.ForeignKey(EventLocation, on_delete=models.SET_NULL, null=True)
    userID = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    def __str__(self):
        return "[orga] {0}".format(self.userID__email)

class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Event(models.Model):
    # eventID = models.AutoField()
    name = models.TextField()
    description = models.TextField()
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    takeplace = models.BooleanField(default=True)
    cost = models.IntegerField()
    promoted = models.BooleanField(default=False)
    starttime = models.DateTimeField()
    endtime = models.DateTimeField()
    mininumage = models.PositiveSmallIntegerField()
    category = models.ManyToManyField(Category)
    def __str__(self):
        return self.name + " [%s]".format(self.organizer__name)



class Participate(models.Model):
    customerID = models.ForeignKey(Customer, on_delete=models.CASCADE)
    eventID = models.ForeignKey(Event, on_delete=models.CASCADE)
    probability = models.PositiveSmallIntegerField()
    def __str__(self):
        return "{0}_{1}".format(self.eventID__name, self.probability)

class EventRating(models.Model):
    # ratingID = models.AutoField()
    rating = models.PositiveSmallIntegerField()
    description = models.TextField()
    customerID = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    eventID = models.ForeignKey(Event, on_delete=models.CASCADE)
    def __str__(self):
        return "{0}_{1}-{2}: {3}".format(self.eventID__name, self.customerID__userID__email, self.description[:75] + (self.description[75:] and '..'))

class EventLocationRating(models.Model):
    # ratingID = models.AutoField()
    rating = models.PositiveSmallIntegerField()
    description = models.TextField()
    customerID = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    eventlocationID = models.ForeignKey(EventLocation, on_delete=models.CASCADE)
    def __str__(self):
        return "{0}_{1}-{2}: {3}".format(self.eventlocationID__name, self.customerID__userID__email, self.description[:75] + (self.description[75:] and '..'))


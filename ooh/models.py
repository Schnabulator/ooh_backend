from django.db import models
import datetime
from django.utils import timezone
from django.views import generic
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
# required for User referencing
from django.conf import settings
from .managers import OohUserManager
from django.utils.translation import ugettext_lazy as _


# Authentication shit
class OohUser(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = "email"
    EMAIL_FIELD    = "email"
    email    = models.EmailField(_('email address'),unique=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    birthday = models.DateField()
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
    plz = models.IntegerField()
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
        


# class User(models.Model):
#     # userID = models.AutoField()
#     ORGANIZER = "organizer"
#     ADMIN = "admin"
#     CUSTOMER ="customer"
#     firstname = models.CharField(max_length=100)
#     lastname = models.CharField(max_length=100)
#     email    = models.EmailField(unique=True)
#     # USERNAME_FIELD = "email"
#     password = models.CharField(max_length=30, default='')
#     birthday = models.DateField()
#     active = models.BooleanField(default=True)
#     last_login = models.DateTimeField(default=timezone.now)
#     REQUIRED_FIELDS = ["firstname", "lastname", "email", "birthday"]

#     def get_full_name(self):
#         return self.firstname+" "+self.lastname
#     def __str__(self):
#         return self.email + " [{0}]".format(self.get_full_name())

# //TODO das darf vllt nicht so gemacht werden
class Customer(models.Model):
    admin = models.BooleanField(default=False)
    # alternativ get_user_model()
    userID = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class Organizer(models.Model):
    location = models.ForeignKey(EventLocation, on_delete=models.SET_NULL, null=True)
    userID = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class Category(models.Model):
    name = models.CharField(max_length=100)

class Event(models.Model):
    # eventID = models.AutoField()
    name = models.TextField()
    description = models.TextField()
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE)

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

class EventRating(models.Model):
    # ratingID = models.AutoField()
    rating = models.PositiveSmallIntegerField()
    description = models.TextField()
    customerID = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    eventID = models.ForeignKey(Event, on_delete=models.CASCADE)

class EventLocationRating(models.Model):
    # ratingID = models.AutoField()
    rating = models.PositiveSmallIntegerField()
    description = models.TextField()
    customerID = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    eventlocationID = models.ForeignKey(EventLocation, on_delete=models.CASCADE)

# class UserManager(BaseUserManager):
#     def create_user(self, firstname, lastname, email, birthday, usertype=0):
#         user = User(firstname, lastname, email, birthday, usertype=0)
#     def create_superuser(self, firstname, lastname, email, birthday):
#         user = User(firstname, lastname, email, birthday, usertype=1)

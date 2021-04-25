from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import OohUserCreationForm, OohUserChangeForm
from .models import Location, EventLocation, Event, OohUser, Participate, EventRating, EventLocationRating, EventCategory, LocationCategory, EventTemplate, Question, ChoiceOption, UserSelection

class CustomUserAdmin(UserAdmin):
    add_form = OohUserCreationForm
    form = OohUserChangeForm
    model = OohUser
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
        ('Personal Data', {'fields': ('birthday', 'firstname', 'lastname','location', 'street', 'housenumber', )}),
    )
    add_fieldsets = (
        # (None, {
        #     'classes': ('wide',),
        #     'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        # ),
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'admin')}),
        ('Personal Data', {'fields': ('birthday', 'firstname', 'lastname','location', 'street', 'housenumber', 'defaultEventLocation', )}),
    )
    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(OohUser, CustomUserAdmin)

class LocationAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['plz', 'cityname', 'bundesland']}),
        # ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    search_fields = ['plz', 'cityname', 'bundesland']
    list_display =  ('plz', 'cityname', 'bundesland')

class ChoiceInline(admin.StackedInline):
    model = ChoiceOption
    fk_name = 'question'
    # extra = 3
class QuestionAdmin(admin.ModelAdmin):
    readonly_fields=('id',)
    fieldsets = [
        (None,               {'fields': ['name', 'firstQuestion', 'lastQuestion', 'priority_in_filtering']}),
        
    ]
    inlines = [ChoiceInline]

admin.site.register(Location, LocationAdmin)
admin.site.register(EventLocation)
admin.site.register(EventTemplate)
admin.site.register(Event)

admin.site.register(Participate)
admin.site.register(EventRating)
admin.site.register(EventLocationRating)
admin.site.register(EventCategory)
admin.site.register(LocationCategory)
admin.site.register(Question, QuestionAdmin)
admin.site.register(ChoiceOption)
admin.site.register(UserSelection)
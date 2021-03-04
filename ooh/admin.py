from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import OohUserCreationForm, OohUserChangeForm
from .models import OohUser


class CustomUserAdmin(UserAdmin):
    add_form = OohUserCreationForm
    form = OohUserChangeForm
    model = OohUser
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
        ('Personal Data', {'fields': ('birthday', 'firstname', 'lastname',)}),
    )
    add_fieldsets = (
        # (None, {
        #     'classes': ('wide',),
        #     'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        # ),
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
        ('Personal Data', {'fields': ('birthday', 'firstname', 'lastname',)}),
    )
    search_fields = ('email',)
    ordering = ('email',)


admin.site.register(OohUser, CustomUserAdmin)
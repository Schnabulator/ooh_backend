from django.urls import path

from . import views

app_name = "ooh"

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='loginview'),
    path('locations/', views.EventLocationView.as_view(), name='locations'),
    path('events/', views.EventView.as_view(), name='events'),
    path('profile/login', views.UserLoginView.as_view(), name='login'),
    path('profile/logout', views.UserLogoutView.as_view(), name='logout'),
    path('profile/', views.UserProfile, name='profile')

    # path('profile/register', views.RegisterView.as_view(), name='register'),
]
from django.urls import path

from . import views

app_name = "oob_api"

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='loginview'),
    path('locations/', views.EventLocationView.as_view(), name='locations'),
    path('events/', views.EventView.as_view(), name='events'),
]
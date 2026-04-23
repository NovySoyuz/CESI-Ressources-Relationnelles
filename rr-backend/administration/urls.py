from . import views
from django.urls import path
from django.http import JsonResponse
from django.urls import include, path

urlpatterns = [
    path('', views.test),
   
]
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [

    path('',views.Home, name = "Home"),
    path('Index',views.Index, name = "Index"),
    path('Result', views.Result, name = 'Result'),

]
from django.urls import path

from app import views

urlpatterns = [
    path('', views.index),
    path('forward', views.forward),
    path('set-status', views.set_status),
]
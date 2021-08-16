from django.urls import path

from app import views

urlpatterns = [
    path('', views.index),
    path('bot/<int:pk>', views.bot_view),
    path('forward', views.forward),
    path('set-status', views.set_status),
]
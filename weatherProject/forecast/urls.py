from django.urls import path
from . import views

urlpatterns = [
    path('weather.html', views.weather_view, name='weather_view'),  # Add this to catch direct .html requests
]

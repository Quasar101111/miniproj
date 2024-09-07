from django.urls import path
from . import views

urlpatterns = [
    path('add-location/', views.add_location, name='add_location'),
    path('location/<int:location_id>/', views.location_details, name='location_details'),
]

#vaultspace/map/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # path('add-location/', views.add_location, name='add_location'),
    # path('location/<int:location_id>/', views.location_details, name='location_details'),
    path('map_view/<int:warehouse_id>/', views.map_view, name='map_view'),
    path('select/', views.select_location, name='select_location'),
]

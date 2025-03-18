#vaultspace/map/urls.py
from django.urls import path
from . import views

app_name = 'map'
urlpatterns = [
    # path('add-location/', views.add_location, name='add_location'),
    # path('location/<int:location_id>/', views.location_details, name='location_details'),
    path('map_view/<int:warehouse_id>/', views.map_view, name='map_view'),
    path('select/', views.select_location, name='select_location'),
    # #test blockchain
    # path('add_warehouse_test/', views.add_warehouse_view, name="add_warehouse"),
    # path('get_warehouse/<int:warehouse_id>/', views.get_warehouse_view, name="get_warehouse"),

    path('recommend_warehouse/', views.recommend_warehouse, name='recommend_warehouse'),

] 

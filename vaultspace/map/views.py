import requests
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import LocationForm
from .models import Location

# Google Maps Geolocation API URL
GOOGLE_MAPS_NEARBY_SEARCH_URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'

# Helper function to get nearby places using Google Places API
def get_nearby_place(lat, lng, place_type, radius=5000):
    params = {
        'location': f'{lat},{lng}',
        'radius': radius,
        'type': place_type,
        'key': settings.GOOGLE_API_KEY
    }
    response = requests.get(GOOGLE_MAPS_NEARBY_SEARCH_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get('results'):
            # Return the first result's name
            return data['results'][0]['name']
    return None

# View to add a location and fetch nearby places
def add_location(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            location = form.save(commit=False)
            
            # Automatically determine nearby main road, airport, and seaport
            latitude = location.latitude
            longitude = location.longitude
            
            # Find nearest main road
            location.nearest_main_road = get_nearby_place(latitude, longitude, 'route')
            
            # Find nearest airport
            location.nearest_airport = get_nearby_place(latitude, longitude, 'airport')
            
            # Find nearest seaport
            location.nearest_seaport = get_nearby_place(latitude, longitude, 'seaport')
            
            location.save()
            messages.success(request, 'Location added successfully with nearby details!')
            return redirect('location_details', location_id=location.id)
    else:
        form = LocationForm()

    return render(request, 'add_location.html', {'form': form, 'google_api_key': settings.GOOGLE_API_KEY})

# View to display location details
def location_details(request, location_id):
    location = get_object_or_404(Location, id=location_id)
    return render(request, 'location_details.html', {
        'location': location,
        'google_api_key': settings.GOOGLE_MAPS_API_KEY
    })
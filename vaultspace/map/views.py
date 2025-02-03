#vaultspace/map/views.py

import requests
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.http import HttpResponseBadRequest
from .models import Map
from warehouse.models import Warehouse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
def get_nearby_features(lat, lon):
    """Fetch nearby roads, railways, and seaports from the Overpass API."""
    overpass_url = "https://overpass.private.coffee/api/interpreter"
    query = f"""
    [out:json];
    (
      way["highway"](around:3000, {lat}, {lon});     // Roads
      way["railway"](around:20000, {lat}, {lon});     // Railways
      node["harbour"](around:50000, {lat}, {lon});    // Seaports
    );
    out center;
    """
    try:
        response = requests.post(overpass_url, data=query)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Overpass API: {e}")
        return None


def map_view(request):
    """Render the map with filtered nearby features."""
    try:
        lat = float(request.GET.get('lat', 11.810711))  # Default latitude
        lon = float(request.GET.get('lon', 75.613307))  # Default longitude
    except ValueError:
        return HttpResponseBadRequest("Invalid latitude or longitude")

    # Fetch nearby features using the helper function
    features = get_nearby_features(lat, lon)

    # Filter for specific types of features: roads, rail, and seaports
    allowed_types = ["road", "rail", "harbour", "seaport", "secondary", "platform"]
    map_data = []
    seen_features = set()  # Track unique features
    unique_features = {}   # Store unique features for modal
    
    if features:
        for feature in features.get("elements", []):
            # Skip if the feature has no name or is named "Unnamed Feature"
            feature_name = feature["tags"].get("name")
            if not feature_name or feature_name == "Unnamed Feature":
                continue
            
            # Create a unique identifier for the feature
            feature_key = f"{feature_name}_{feature['tags'].get('highway', feature['tags'].get('railway', ''))}"
            
            # Skip if we've already seen this feature
            if feature_key in seen_features:
                continue
            
            seen_features.add(feature_key)
                
            if feature["type"] == "node":  # For nodes like seaports
                feature_type = feature["tags"].get("man_made", feature["tags"].get("amenity", "")).lower()
                if feature_type in ["harbour", "seaport"]:
                    feature_data = {
                        "lat": feature["lat"],
                        "lon": feature["lon"],
                        "name": feature_name,
                        "type": "Harbour"
                    }
                    map_data.append(feature_data)
                    unique_features[feature_key] = feature_data
                        
            elif feature["type"] == "way" and "center" in feature:  # For ways like roads/railways
                feature_type = feature["tags"].get("highway", feature["tags"].get("railway", "")).lower()
                if feature_type in allowed_types:
                    modal_type = "Road" if feature_type.lower() == "secondary" else feature_type.capitalize()
                    map_type = feature_type.capitalize()  # Keep original type for map icons
        
                    feature_data = {
                        "lat": feature["center"]["lat"],
                        "lon": feature["center"]["lon"],
                        "name": feature_name,
                        "type": map_type,  # For map icons
                        "display_type": modal_type  # For modal display
                    }
                    map_data.append(feature_data)
                    unique_features[feature_key] = feature_data

    # Convert unique features dictionary to list for modal
    modal_data = list(unique_features.values())

    # Sort modal data by type and name
    modal_data.sort(key=lambda x: (x['type'], x['name']))

    # Render the map page with both datasets
    return render(request, 'map/map_view.html', {
        'map_data': map_data,      # All features for the map
        'modal_data': modal_data,  # Unique features for the modal
        'lat': lat, 
        'lon': lon
    })


# def select_location(request):
#     warehouse_id = 10
#     if not warehouse_id:
#         messages.error(request, 'Warehouse ID is required')
#         # return redirect('warehouse_list')  # Redirect to warehouse list if no ID provided
    
#     try:
#         warehouse = Warehouse.objects.get(warehouse_id=warehouse_id)
#         # Get existing map location if any
#         map_location = Map.objects.filter(warehouse_id=warehouse_id).first()
#         initial_lat = float(map_location.latitude) if map_location else 11.810711
#         initial_lon = float(map_location.longitude) if map_location else 75.613307
#     except Warehouse.DoesNotExist:
#         messages.error(request, 'Warehouse not found')
#         return redirect('warehouse_list')

#     context = {
#         'warehouse': warehouse,
#         'initial_lat': initial_lat,
#         'initial_lon': initial_lon,
#     }
#     return render(request, 'map/select_location.html', context)

# def save_location(request):
#     if request.method == 'POST':
#         try:
#             warehouse_id = request.POST.get('warehouse_id')
#             latitude = request.POST.get('latitude')
#             longitude = request.POST.get('longitude')
            
#             # Update or create map location
#             map_obj, created = Map.objects.update_or_create(
#                 warehouse_id=warehouse_id,
#                 defaults={
#                     'latitude': latitude,
#                     'longitude': longitude
#                 }
#             )
            
#             return JsonResponse({
#                 'status': 'success',
#                 'message': 'Location saved successfully'
#             })
#         except Exception as e:
#             return JsonResponse({
#                 'status': 'error',
#                 'message': str(e)
#             }, status=400)
    
#     return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def select_location(request):
    """Handle location selection and saving."""
    if request.method == 'POST':
        try:
            warehouse_id = request.POST.get('warehouse_id')
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            
            # Validate inputs
            if not all([warehouse_id, latitude, longitude]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Missing required fields'
                }, status=400)

            # Get or create warehouse
            try:
                warehouse = Warehouse.objects.get(warehouse_id=warehouse_id)
            except Warehouse.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Warehouse not found'
                }, status=404)

            # Update or create map location
            map_obj, created = Map.objects.update_or_create(
                warehouse=warehouse,
                defaults={
                    'latitude': latitude,
                    'longitude': longitude
                }
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Location saved successfully',
                'data': {
                    'latitude': str(map_obj.latitude),
                    'longitude': str(map_obj.longitude)
                }
            })
            
        except Exception as e:
            print(f"Error saving location: {str(e)}")  # For debugging
            return JsonResponse({
                'status': 'error',
                'message': f'Error saving location: {str(e)}'
            }, status=400)
    
    # For GET requests, render the template
    return render(request, 'map/select_location.html')
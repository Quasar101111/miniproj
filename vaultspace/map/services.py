# map/services.py
import httpx
from django.conf import settings
from typing import List
from asgiref.sync import sync_to_async
from django.shortcuts import render
from django.http import HttpResponseBadRequest
from users.models import Tenant
from map.models import Map
from warehouse.models import Warehouse

async def get_recommendations(tenant, warehouses: List, limit: int = 5):
    async with httpx.AsyncClient() as client:
        try:
            # Get warehouse map data
            warehouse_maps = await sync_to_async(list)(
                Map.objects.filter(warehouse__in=warehouses)
            )
            
            # Create a dictionary to quickly look up maps by warehouse
            map_dict = {map_obj.warehouse_id: map_obj for map_obj in warehouse_maps}
            
            # Prepare request data
            data = {
                "tenant": {
                    "id": tenant.id,
                    "latitude": float(tenant.latitude) if hasattr(tenant, 'latitude') else None,
                    "longitude": float(tenant.longitude) if hasattr(tenant, 'longitude') else None,
                    "lease_history_count": await sync_to_async(
                        lambda: tenant.lease_set.count()
                    )()
                },
                "available_warehouses": [
                    {
                        "id": w.warehouse_id,
                        "length": float(w.length) if w.length else 0,
                        "width": float(w.breadth) if w.breadth else 0,  # Fixed: breadth instead of width
                        "height": float(w.height) if w.height else 0,
                        "latitude": float(map_dict[w.warehouse_id].latitude) if w.warehouse_id in map_dict else 0,
                        "longitude": float(map_dict[w.warehouse_id].longitude) if w.warehouse_id in map_dict else 0,
                        "rental_price": float(w.rental_price),
                        "facilities": w.facilities.split(',') if w.facilities else [],
                        "year_built": w.year_built.strftime('%Y-%m-%d') if w.year_built else None
                    }
                    for w in warehouses if w.warehouse_id in map_dict
                ]
            }
           
            response = await client.post(
                f"{settings.RECOMMENDER_API_URL}/recommend/",
                json=data,
                params={"limit": limit}
            )
            response.raise_for_status()  # Fixed: raise_for_status instead of raise_for_async
           
            return response.json()
           
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []

async def recommend_warehouse(request):
    try:
        # Use sync_to_async for database operations
        tenant = await sync_to_async(Tenant.objects.get)(
            email='agustine02343zxxx@gmail.com'
        )
       
        # Fetch warehouses asynchronously
        warehouses = await sync_to_async(list)(
            Warehouse.objects.filter(status=1)
        )
       
        # Get recommendations from the API
        api_recommendations = await get_recommendations(tenant, warehouses, limit=5)
        
        # If API returns recommendations, use them
        if api_recommendations:
            # Fetch maps for warehouses that are in the recommendations
            recommended_warehouse_ids = [rec['warehouse_id'] for rec in api_recommendations]
            warehouse_maps = await sync_to_async(list)(
                Map.objects.filter(warehouse_id__in=recommended_warehouse_ids)
                .select_related('warehouse')
            )
            
            # Create a dictionary to quickly access maps
            maps_dict = {map_obj.warehouse_id: map_obj for map_obj in warehouse_maps}
            
            recommendations = [
                {
                    "warehouse_id": rec['warehouse_id'],
                    "name": maps_dict[rec['warehouse_id']].warehouse.name if rec['warehouse_id'] in maps_dict else "Unknown",
                    "location": maps_dict[rec['warehouse_id']].warehouse.location if rec['warehouse_id'] in maps_dict else None,
                    "rental_price": float(maps_dict[rec['warehouse_id']].warehouse.rental_price) if rec['warehouse_id'] in maps_dict else 0,
                    "area": float(maps_dict[rec['warehouse_id']].warehouse.area) if rec['warehouse_id'] in maps_dict else 0,
                    "status": maps_dict[rec['warehouse_id']].warehouse.status if rec['warehouse_id'] in maps_dict else 0,
                    "similarity_score": rec.get('similarity_score', 0),
                    "ranking": idx + 1,
                    "lat": float(maps_dict[rec['warehouse_id']].latitude) if rec['warehouse_id'] in maps_dict else 0,
                    "lng": float(maps_dict[rec['warehouse_id']].longitude) if rec['warehouse_id'] in maps_dict else 0
                }
                for idx, rec in enumerate(api_recommendations)
            ]
        else:
            # Fallback: Just use the first 5 warehouses with their maps
            warehouse_maps = await sync_to_async(list)(
                Map.objects.filter(warehouse__in=warehouses[:5])
                .select_related('warehouse')
            )
            
            recommendations = [
                {
                    "warehouse_id": map_obj.warehouse.warehouse_id,
                    "name": map_obj.warehouse.name,
                    "location": map_obj.warehouse.location,
                    "rental_price": float(map_obj.warehouse.rental_price),
                    "area": float(map_obj.warehouse.area),
                    "status": map_obj.warehouse.status,
                    "similarity_score": 0.95 - (idx * 0.05),  # Example score with decreasing values
                    "ranking": idx + 1,
                    "lat": float(map_obj.latitude),
                    "lng": float(map_obj.longitude)
                }
                for idx, map_obj in enumerate(warehouse_maps)
            ]
       
        return render(request, 'map/recommend_warehouse.html', {
            'recommendations': recommendations
        })
   
    except Exception as e:
        return HttpResponseBadRequest(f"Error: {str(e)}")
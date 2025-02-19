import json
from django.shortcuts import render
from django.http import HttpResponse
from .models import Tenant,User  # Import relevant models
from warehouse.models import Warehouse

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

import requests
from django.conf import settings


import numpy as np
# from .ml_model import model_loader  # Ensure m
from django.core.cache import cache

@login_required
@require_http_methods(["POST"])
def update_location(request):
    try:
        user = request.user
        
        # Get tenant using the same logic as login view
        tenant = Tenant.objects.get(email=user.email)
        
        # Update session like in login view
        request.session['tenant_id'] = tenant.tenant_id
        request.session.save()

        data = json.loads(request.body)
        
        # Update location coordinates
        tenant.latitude = data['latitude']
        tenant.longitude = data['longitude']
        tenant.save()

        return JsonResponse({
            'success': True,
            'message': 'Location updated '
        })

    except Tenant.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Tenant profile not found. Please complete your profile.',
            'redirect': '/tenant_details/'
        }, status=404)
    except KeyError as e:
        return JsonResponse({
            'success': False,
            'message': f'Missing required field: {str(e)}'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)
    

def get_recommendations(request, tenant_id):
    """
    Handle recommendation requests for specific tenants
    """
    cache_key = f"recs_{tenant_id}"
    
    # Try cache first
    if cached := cache.get(cache_key):
        return JsonResponse({'recommendations': cached, 'source': 'cache'})
    
    try:
        # Get model instance
        model = model_loader.model
        if not model:
            raise ValueError("Model not loaded")
            
        # Get candidate warehouses
        candidates = Warehouse.objects.filter(is_available=True)[:100]
        if not candidates:
            return JsonResponse({'recommendations': []})
            
        # Prepare input data
        features = self._prepare_features(tenant_id, candidates)
        
        # Get predictions
        predictions = model.predict(features).flatten()
        sorted_indices = np.argsort(predictions)[::-1]
        recommendations = [candidates[i].warehouse_id for i in sorted_indices[:5]]
        
        # Cache results for 1 hour
        cache.set(cache_key, recommendations, 3600)
        
        return JsonResponse({
            'recommendations': recommendations,
            'source': 'model',
            'tenant_id': str(tenant_id)
        })
        
    except Exception as e:
        # Fallback to popular warehouses
        fallback = list(Warehouse.objects
            .filter(is_available=True)
            .order_by('-rating', '-created_at')
            .values_list('warehouse_id', flat=True)[:5])
            
        return JsonResponse({
            'recommendations': fallback,
            'source': 'fallback',
            'message': f'Using fallback: {str(e)}'
        })

    def _prepare_features(self, tenant_id, candidates):
        # Get facility choices from the model
        FACILITY_OPTIONS = [
            'security', 'climate_control', 'parking', 
            'loading_dock', 'fire_safety', 'insurance',
            '24hr_access', 'forklift', 'alarm_system',
            'surveillance'
        ]
        
        return {
            "tenant_id": [tenant_id] * len(candidates),
            "warehouse_id": [wh.warehouse_id for wh in candidates],
            "numerical_features": np.array([
                [
                    float(wh.area),
                    float(wh.length) if wh.length else 0.0,
                    float(wh.breadth) if wh.breadth else 0.0,
                    float(wh.height) if wh.height else 0.0,
                    float(wh.rental_price)
                ] for wh in candidates
            ]),
            "facilities": np.array([
                [
                    1.0 if facility in wh.facilities.split(',') else 0.0 
                    for facility in FACILITY_OPTIONS
                ] for wh in candidates
            ])
        }
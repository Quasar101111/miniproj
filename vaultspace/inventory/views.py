# Create your views here.
# inventory/views.py
from django.shortcuts import render, redirect, get_object_or_404
from warehouse.models import Warehouse
from .models import Zone, InventoryItem, InventoryLocation,WarehouseUsage
from django.core.exceptions import ValidationError
from decimal import Decimal
import json
from django.core.serializers import serialize
from django.http import JsonResponse
from django.db.models import Sum, IntegerField
from django.db.models.functions import Coalesce  # Correct location for Coalesce
from django.db.models import F
def calculate_available_dimensions(warehouse):
    """Calculate the available dimensions and area of the warehouse."""
    # Debug: Print warehouse details
    print(f"Debug: Warehouse ID: {warehouse.warehouse_id}, Length: {warehouse.length}, Breadth: {warehouse.breadth}, Height: {warehouse.height}")
    
    # Get the warehouse usage instance
    warehouse_usage = warehouse.usage
    print(f"Debug: WarehouseUsage instance: {warehouse_usage}")
    
    # Access the usage values correctly
    used_length = warehouse_usage.used_length
    used_breadth = warehouse_usage.used_breadth
    used_height = warehouse_usage.used_height
    print(f"Debug: Used dimensions - Length: {used_length}, Breadth: {used_breadth}, Height: {used_height}")
    
    # Calculate available dimensions
    available_length = warehouse.length - used_length
    available_breadth = warehouse.breadth - used_breadth
    available_height = warehouse.height - used_height
    print(f"Debug: Available dimensions - Length: {available_length}, Breadth: {available_breadth}, Height: {available_height}")
    
    # Calculate available area
    available_area = available_length * available_breadth
    print(f"Debug: Available area: {available_area}")
    
    return available_length, available_breadth, available_height, available_area

def calculate_zone_data(zone, warehouse):
    """
    Calculate all required data for a zone:
    - Used dimensions (length, breadth, height)
    - Usage percentage (based on volume)
    - Warehouse utilization (percentage of warehouse dimensions)
    """
    # Debug: Print zone and warehouse details
    print(f"Debug: Zone ID = {zone.id}, Name = {zone.name}")
    print(f"Debug: Warehouse ID = {warehouse.warehouse_id}, Name = {warehouse.name}")

    # Calculate used dimensions
    used_length = Decimal('0.0')
    used_breadth = Decimal('0.0')
    used_height = Decimal('0.0')
    for location in zone.locations.all():
        print(f"Debug: Location ID = {location.id}, Length = {location.length}, Width = {location.width}, Height = {location.height}")
        used_length += Decimal(str(location.length))
        used_breadth += Decimal(str(location.width))
        used_height += Decimal(str(location.height))

    # Debug: Print used dimensions
    print(f"Debug: Used Length = {used_length}, Used Breadth = {used_breadth}, Used Height = {used_height}")

    # Calculate usage percentage (based on volume)
    total_volume = zone.length * zone.breadth * zone.height
    used_volume = used_length * used_breadth * used_height
    usage_percentage = (used_volume / total_volume) * 100 if total_volume else 0.0

    # Debug: Print volume calculations
    print(f"Debug: Total Volume = {total_volume}, Used Volume = {used_volume}, Usage Percentage = {usage_percentage}")

    # Calculate warehouse utilization (percentage of warehouse dimensions)
    length_utilization = (zone.length / warehouse.length) * 100 if warehouse.length else 0
    breadth_utilization = (zone.breadth / warehouse.breadth) * 100 if warehouse.breadth else 0
    height_utilization = (zone.height / warehouse.height) * 100 if warehouse.height else 0

    # Debug: Print warehouse utilization
    print(f"Debug: Length Utilization = {length_utilization}%, Breadth Utilization = {breadth_utilization}%, Height Utilization = {height_utilization}%")

    return {
        'used_length': float(used_length),
        'used_breadth': float(used_breadth),
        'used_height': float(used_height),
        'usage_percentage': float(usage_percentage),
        'warehouse_utilization': {
            'length': float(length_utilization),
            'breadth': float(breadth_utilization),
            'height': float(height_utilization),
        }
    }

def get_item_location_data(warehouse):
    items = InventoryItem.objects.filter(
        warehouse=warehouse
    ).annotate(
        total_in_locations=Coalesce(
            Sum('inventorylocation__item_count'),
            0,
            output_field=IntegerField()
        )
    ).values('id', 'name', 'total_in_locations')
    
    locations = InventoryLocation.objects.filter(
        zone__warehouse=warehouse
    ).select_related('item', 'zone').values(
        'id', 'zone__name', 'item_id', 'item_count'
    )
    
    return {
        'items': list(items),
        'locations': list(locations)
    }

def get_zone_utilization_alerts(warehouse, warning_threshold=90, underutilized_threshold=30):
    alerts = []
    zones = Zone.objects.filter(warehouse=warehouse)
    
    for zone in zones:
        zone_data = calculate_zone_data(zone, warehouse)
        usage_percentage = zone_data['usage_percentage']
        
        if usage_percentage >= warning_threshold:
            alerts.append({
                'zone': zone.name,
                'type': 'warning',
                'message': f"{zone.name} is {usage_percentage:.1f}% full - nearing capacity",
                'usage': usage_percentage
            })
        elif usage_percentage <= underutilized_threshold:
            alerts.append({
                'zone': zone.name,
                'type': 'info',
                'message': f"{zone.name} is underutilized ({usage_percentage:.1f}% full)",
                'usage': usage_percentage
            })
    
    # Sort by severity (warning first, then underutilized)
    return sorted(alerts, key=lambda x: (-x['usage'] if x['type'] == 'warning' else x['usage']))

def insert_data(request, warehouse_id):
    context = {}
    
    warehouse = Warehouse.objects.get(warehouse_id=warehouse_id)
    
    # Initialize usage if it doesn't exist
    if not hasattr(warehouse, 'usage'):
        WarehouseUsage.objects.create(warehouse=warehouse)
    
    # Calculate available dimensions
    available_length, available_breadth, available_height, _ = calculate_available_dimensions(warehouse)

    # Get zones with calculated data
    warehouse_zones = Zone.objects.filter(warehouse=warehouse)
    
    # Get items only from this warehouse's locations
    inventory_items = InventoryItem.objects.filter(
        inventorylocation__zone__warehouse=warehouse
    ).distinct()

    # Prepare zone data for both context and JSON
    zones_data = []
    for zone in warehouse_zones:
        zone_data = {
            'id': zone.id,
            'name': zone.name,
            'length': float(zone.length) if isinstance(zone.length, Decimal) else zone.length,
            'breadth': float(zone.breadth) if isinstance(zone.breadth, Decimal) else zone.breadth,
            'height': float(zone.height) if isinstance(zone.height, Decimal) else zone.height,
            **calculate_zone_data(zone, warehouse)
        }
        zones_data.append(zone_data)
        # Attach calculated data to the zone object for template use
        zone.usage_percentage = zone_data['usage_percentage']
        zone.used_length = zone_data['used_length']
        zone.used_breadth = zone_data['used_breadth']
        zone.used_height = zone_data['used_height']

    # Serialize the prepared data
    warehouse_zones_json = json.dumps(zones_data)
    print("Debug: warehouse_zones_json =", warehouse_zones_json)

    # Add all variables to context
    context.update({
        'warehouse_zones_json': warehouse_zones_json,
        'warehouse_zones': warehouse_zones,  # Now includes calculated data
        'available_length': available_length,
        'available_breadth': available_breadth,
        'available_height': available_height,
        'warehouse': warehouse,
        'inventory_items': inventory_items,
        'item_location_data': get_item_location_data(warehouse),
        'utilization_alerts': get_zone_utilization_alerts(warehouse),
    })

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        try:
            if form_type == 'zone':
                name = request.POST.get('zone_name')
                zone_type = request.POST.get('zone_type')
                length = Decimal(request.POST.get('zone_length'))
                breadth = Decimal(request.POST.get('zone_breadth'))
                height = Decimal(request.POST.get('zone_height'))
                
                # Validate dimensions
                if length > available_length or breadth > available_breadth or height > available_height:
                    raise ValidationError("Zone dimensions exceed available warehouse dimensions.")
                
                # Create zone
                zone = Zone.objects.create(
                    name=name,
                    zone_type=zone_type,
                    length=length,
                    breadth=breadth,
                    height=height,
                    warehouse=warehouse
                )
                
                warehouse_usage = warehouse.usage
                # print('###################')
                # print(f"Debug: Before update - Used Length: {warehouse_usage.used_length}, Used Breadth: {warehouse_usage.used_breadth}, Used Height: {warehouse_usage.used_height}")

                # Update the used dimensions
                warehouse_usage.used_length = Decimal(str(warehouse_usage.used_length)) + length
                warehouse_usage.used_breadth = Decimal(str(warehouse_usage.used_breadth)) + breadth
                warehouse_usage.used_height = Decimal(str(warehouse_usage.used_height)) + height
                warehouse_usage.save()

                # print(f"Debug: After update - Used Length: {warehouse_usage.used_length}, Used Breadth: {warehouse_usage.used_breadth}, Used Height: {warehouse_usage.used_height}")
                # print(f"Debug: Zone dimensions - Length: {length}, Breadth: {breadth}, Height: {height}")

            
            elif form_type == 'item':
                name = request.POST.get('item_name')
                item_length = float(request.POST.get('item_length'))
                item_width = float(request.POST.get('item_width'))
                item_height = float(request.POST.get('item_height'))
                
                InventoryItem.objects.create(
                    name=name,
                    item_length=item_length,
                    item_width=item_width,
                    item_height=item_height,
                    warehouse=warehouse  # Set warehouse automatically
                )
                return redirect('insert_data', warehouse_id=warehouse_id)
            
            elif form_type == 'location':
                zone_id = int(request.POST.get('location_zone'))
                item_id = request.POST.get('location_item')
                length = float(request.POST.get('location_length'))
                width = float(request.POST.get('location_width'))
                height = float(request.POST.get('location_height'))
                stackable = request.POST.get('stackable') == 'on'
                max_stacking_height = 0.0  # Default value
                
                try:
                    if stackable:
                        # Only process if stackable is checked
                        max_stacking_height_str = request.POST.get('max_stacking_height')
                        if max_stacking_height_str:
                            max_stacking_height = float(max_stacking_height_str)
                        else:
                            raise ValidationError("Max stacking height required when stackable is checked")
                
                except ValueError as e:
                    return render(request, 'inventory/insert_data.html', {
                        **context, 
                        'error': f"Invalid stacking height: {str(e)}"
                    })
                
                item_count = int(request.POST.get('item_count'))
                
                zone = Zone.objects.get(id=zone_id)
                item = InventoryItem.objects.get(id=item_id) if item_id else None
                location = InventoryLocation(
                    zone=zone, item=item, length=length, width=width, height=height,
                    stackable=stackable, max_stacking_height=max_stacking_height, item_count=item_count
                )
                location.save()
        
        except ValidationError as e:
            return render(request, 'inventory/insert_data.html', {**context, 'error': e.message})
        return redirect('insert_data',warehouse_id=warehouse_id)
    
    return render(request, 'inventory/insert_data.html', context)

def get_item_details(request, item_id):
    try:
        item = InventoryItem.objects.get(id=item_id)
        return JsonResponse({
            'item_length': item.item_length,
            'item_width': item.item_width,
            'item_height': item.item_height,
        })
    except InventoryItem.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)

def warehouse_dashboard(request):
    context = {}
    
    warehouse = Warehouse.objects.get(warehouse_id=10)
    
    # Initialize usage if it doesn't exist
    if not hasattr(warehouse, 'usage'):
        WarehouseUsage.objects.create(warehouse=warehouse)
    
    # Calculate available dimensions
    available_length, available_breadth, available_height, _ = calculate_available_dimensions(warehouse)

    warehouse_zones = Zone.objects.filter(warehouse=warehouse)

    # Serialize warehouse zones with usage data
    warehouse_zones_json = json.dumps([
        {
            'id': zone.id,
            'name': zone.name,
            'length': float(zone.length) if isinstance(zone.length, Decimal) else zone.length,
            'breadth': float(zone.breadth) if isinstance(zone.breadth, Decimal) else zone.breadth,
            'height': float(zone.height) if isinstance(zone.height, Decimal) else zone.height,
            **calculate_zone_data(zone, warehouse)  # Include calculated data
        }
        for zone in warehouse_zones
    ])

    # Add all variables to context
    context.update({
        'warehouse_zones': json.loads(warehouse_zones_json),
        'available_length': available_length,
        'available_breadth': available_breadth,
        'available_height': available_height,
        'warehouse': warehouse,
        'utilization_alerts': get_zone_utilization_alerts(warehouse),
    })

    return render(request, 'inventory/warehouse_dashboard.html', context)

def get_zone_items(request, zone_id):
    try:
        zone = get_object_or_404(Zone, id=zone_id)
        items = InventoryItem.objects.filter(
            warehouse=zone.warehouse
        ).values(
            'id', 'name', 
            'item_length', 'item_width', 'item_height'
        )
        
        return JsonResponse({
            'items': [
                {
                    'id': item['id'],
                    'name': item['name'],
                    'dimensions': f"{item['item_length']}m × {item['item_width']}m × {item['item_height']}m",
                    'item_length': item['item_length'],
                    'item_width': item['item_width'],
                    'item_height': item['item_height']
                }
                for item in items
            ]
        })
    except Exception as e:
        print(f"Error in get_zone_items: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)




def warehouse_data(request):
    warehouses = Warehouse.objects.all()
    data = []

    for warehouse in warehouses:
        zones = Zone.objects.filter(warehouse=warehouse)
        zone_data = []

        for zone in zones:
            locations = InventoryLocation.objects.filter(zone=zone)
            location_data = [
                {
                    "id": loc.id,
                    "length": loc.length,
                    "width": loc.width,
                    "height": loc.height,
                    "stackable": loc.stackable,
                    "max_stacking_height": loc.max_stacking_height,
                    "item_count": loc.item_count,
                }
                for loc in locations
            ]

            zone_data.append({
                "name": zone.name,
                "type": zone.zone_type,
                "length": zone.length,
                "breadth": zone.breadth,
                "height": zone.height,
                "locations": location_data
            })

        data.append({
            "warehouse_id": warehouse.id,
            "name": warehouse.name,
            "length": warehouse.length,
            "breadth": warehouse.breadth,
            "height": warehouse.height,
            "zones": zone_data
        })

    return JsonResponse(data, safe=False)

def warehouse_3d_view(request):
    warehouse = get_object_or_404(Warehouse, warehouse_id=10)
    # Prefetch related zones and their locations with items
    warehouse = Warehouse.objects.prefetch_related(
        'zones',
        'zones__locations',
        'zones__locations__item'
    ).get(warehouse_id=9)
    
    return render(request, 'inventory/3d_view.html', {
        'warehouse': warehouse
    })

def map_view(request, warehouse_id):
    warehouse = get_object_or_404(Warehouse, warehouse_id=warehouse_id)
    
    return render(request, 'map/map_view.html', {
        'warehouse': warehouse,
    })
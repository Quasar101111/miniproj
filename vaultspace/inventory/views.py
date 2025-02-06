# Create your views here.
# inventory/views.py
from django.shortcuts import render, redirect
from warehouse.models import Warehouse
from .models import Zone, InventoryItem, InventoryLocation,WarehouseUsage
from django.core.exceptions import ValidationError
from decimal import Decimal
import json
from django.core.serializers import serialize


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

def insert_data(request):
    context = {}
    
    warehouse = Warehouse.objects.get(warehouse_id=10)
    warehouse_zones = Zone.objects.filter(warehouse=warehouse)
    inventory_items = InventoryItem.objects.all()
    
    # Initialize usage if it doesn't exist
    if not hasattr(warehouse, 'usage'):
        WarehouseUsage.objects.create(warehouse=warehouse)
    
    # Calculate available dimensions
    available_length, available_breadth, available_height, _ = calculate_available_dimensions(warehouse)

    # Calculate available space for each zone
    for zone in warehouse_zones:
        # Convert sums to Decimal for consistent calculations
        zone_used_length = Decimal(str(sum(float(location.length) for location in zone.locations.all())))
        zone_used_width = Decimal(str(sum(float(location.width) for location in zone.locations.all())))
        zone_used_height = Decimal(str(sum(float(location.height) for location in zone.locations.all())))

        # Perform calculations using Decimal
        zone.available_length = Decimal(str(zone.length)) - zone_used_length
        zone.available_width = Decimal(str(zone.breadth)) - zone_used_width
        zone.available_height = Decimal(str(zone.height)) - zone_used_height

    # Convert zones to JSON including usage data
    warehouse_zones_json = json.dumps([
        {
            'id': zone.id,
            'name': zone.name,
            'length': float(zone.length),
            'breadth': float(zone.breadth),
            'height': float(zone.height),
            'used_length': float(zone_used_length),  # Use the calculated value
            'used_breadth': float(zone_used_width),  # Use the calculated value
            'used_height': float(zone_used_height),  # Use the calculated value
        }
        for zone in warehouse_zones
    ])
    print("Debug: warehouse_zones_json =", warehouse_zones_json)  # Check if it's empty

    
    # Add all variables to context
    context.update({
        'warehouse_zones_json': warehouse_zones_json,
        'available_length': available_length,
        'available_breadth': available_breadth,
        'available_height': available_height,
        'warehouse': warehouse,
        'warehouse_zones': warehouse_zones,
        'inventory_items': inventory_items,
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
                InventoryItem.objects.create(name=name, item_length=item_length, item_width=item_width, item_height=item_height)
            
            elif form_type == 'location':
                zone_id = int(request.POST.get('location_zone'))
                item_id = request.POST.get('location_item')
                length = float(request.POST.get('location_length'))
                width = float(request.POST.get('location_width'))
                height = float(request.POST.get('location_height'))
                stackable = request.POST.get('stackable') == 'on'
                max_stacking_height = float(request.POST.get('max_stacking_height'))
                
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
        return redirect('insert_data')
    
    return render(request, 'inventory/insert_data.html', context)
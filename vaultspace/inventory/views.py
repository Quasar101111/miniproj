# Create your views here.
# inventory/views.py
from django.shortcuts import render, redirect
from warehouse.models import Warehouse
from .models import Zone, InventoryItem, InventoryLocation,WarehouseUsage
from django.core.exceptions import ValidationError


def calculate_available_dimensions(warehouse):
    """Calculate the available dimensions and area of the warehouse."""
    used_length = warehouse.usage.used_length
    used_breadth = warehouse.usage.used_breadth
    used_height = warehouse.usage.used_height

    available_length = warehouse.length - used_length
    available_breadth = warehouse.breadth - used_breadth
    available_height = warehouse.height - used_height

    available_area = available_length * available_breadth

    return available_length, available_breadth, available_height, available_area

def insert_data(request):
    # Get the warehouse (you'll need to adjust this based on your setup)
    warehouse = Warehouse.objects.first()  # or however you select the warehouse
    
    # Calculate available dimensions
    if warehouse:
        if not hasattr(warehouse, 'usage'):
            WarehouseUsage.objects.create(warehouse=warehouse)
        available_length, available_breadth, available_height, available_area = calculate_available_dimensions(warehouse)
    else:
        available_length = available_breadth = available_height = available_area = 0

    context = {
        'available_length': available_length,
        'available_breadth': available_breadth,
        'available_height': available_height,
        'available_area': available_area,
        'warehouse': warehouse,
    }

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        try:
            if form_type == 'zone':
                
                name = request.POST.get('zone_name')
                print("POST data:", request.POST)  
                zone_type = request.POST.get('zone_type')
                length_str = request.POST.get('zone_length')
                width_str = request.POST.get('zone_breadth')
                height_str = request.POST.get('zone_height')
                warehouse_id = int(request.POST.get('warehouse_id'))
                warehouse = Warehouse.objects.get(pk=warehouse_id)
                
                length = float(length_str)
                breadth = float(width_str)
                height = float(height_str)

                
                if not hasattr(warehouse, 'usage'):
                    WarehouseUsage.objects.create(warehouse=warehouse)
                
                # Calculate available dimensions
                available_length, available_breadth, available_height, _ = calculate_available_dimensions(warehouse)
                
                # Check if the zone dimensions fit within the available warehouse dimensions
                if length > available_length or breadth > available_breadth or height > available_height:
                    raise ValidationError("Zone dimensions exceed available warehouse dimensions.")
                
                
                Zone.objects.create(name=name, zone_type=zone_type, length=length, breadth=breadth, height=height, warehouse=warehouse)
            
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
                aisle_width = float(request.POST.get('aisle_width'))
                item_count = int(request.POST.get('item_count'))
                
                zone = Zone.objects.get(id=zone_id)
                item = InventoryItem.objects.get(id=item_id) if item_id else None
                location = InventoryLocation(
                    zone=zone, item=item, length=length, width=width, height=height,
                    stackable=stackable, max_stacking_height=max_stacking_height, aisle_width=aisle_width, item_count=item_count
                )
                location.save()
        
        except ValidationError as e:
            return render(request, 'inventory/insert_data.html', {**context, 'error': e.message})
        return redirect('insert_data')
    
    return render(request, 'inventory/insert_data.html', context)
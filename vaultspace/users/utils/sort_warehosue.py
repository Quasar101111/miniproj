from warehouse.models import Warehouse

def sort_warehouses(warehouses, sort_option):
    if sort_option == 'price_asc':
        return warehouses.order_by('rental_price')
    elif sort_option == 'price_desc':
        return warehouses.order_by('-rental_price')
    elif sort_option == 'date_desc':
        return warehouses.order_by('-year_built')
    elif sort_option == 'date_asc':
        return warehouses.order_by('year_built')
    elif sort_option == 'available_places':
        return warehouses.order_by('-available_places')  # Assuming you have an 'available_places' field
    elif sort_option == 'area':
        return warehouses.order_by('area')  # Assuming you have an 'area' field
    else:
        return warehouses.order_by('-warehouse_id')  # Default sorting
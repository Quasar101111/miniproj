# warehouse/views.py


from django.shortcuts import render
from datetime import datetime
from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from .forms import WarehouseForm, WarehousePhotoForm
from .models import Warehouse, WarehousePhoto,Location
from users.models import Lessor, Profile,User
from users.views import lessor_index
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now

@login_required
def add_warehouse(request):
    locations = Location.objects.all()
    lessor_id = request.session.get('lessor_id')
    lessor=Lessor.objects.get(lessor_id=lessor_id)
    today = now().date()
    if request.method == 'POST':
        location_id = request.POST.get('location')
        area = request.POST.get('area')
        ownership_document = request.FILES.get('ownership_document')
        landmark = request.POST.get('landmark')
        rental_price = request.POST.get('rental_price')
        terms_cond = request.POST.get('terms_cond')
        facilities = request.POST.getlist('facilities')
        images = request.FILES.getlist('images')
        date = request.POST.get('date')
        date_obj = datetime.strptime(date, "%d %B, %Y")
        formatted_date = date_obj.strftime("%Y-%m-%d")
        
        if location_id and area and rental_price:
            location = Location.objects.get(pk=location_id)
            # Retrieve lessor ID from session
            
            if lessor_id:
                lessor = Lessor.objects.get(pk=lessor_id)
                warehouse = Warehouse.objects.create(
                    owner=lessor,
                    location=location,
                    area=area,
                    ownership_documents=ownership_document,
                    landmarks=landmark,
                    year_built=date_obj,
                    rental_price=rental_price,
                    terms_cond=terms_cond,
                    facilities=','.join(facilities),
                    status=1  # Default status
                )

                for image in images:
                    WarehousePhoto.objects.create(warehouse=warehouse, image=image)

                return redirect('lessor_index')

    return render(request, 'warehouse/add_warehouse.html', {'locations': locations,'lessor_id': lessor_id,'lessor': lessor})
@login_required
def temp1(request):
    locations = Location.objects.all()
    lessor_id = request.session.get('lessor_id')
    lessor = Lessor.objects.get(lessor_id=lessor_id)
    warehouses = Warehouse.objects.filter(owner=lessor_id)
    
    print("Locations:", locations)
    print("Lessor ID:", lessor_id)
    print("Lessor:", lessor)
    print("Warehouses:", warehouses)
    
    return render(request, 'warehouse/temp1.html', {
        'locations': locations,
        'lessor_id': lessor_id,
        'lessor': lessor,
        'warehouses': warehouses
    })
def edit_warehouse(request, warehouse_id):
    warehouse = Warehouse.objects.get(warehouse_id=warehouse_id)
    locations = Location.objects.all()
    lessor_id = request.session.get('lessor_id')
    lessor = Lessor.objects.get(lessor_id=lessor_id)
    # Split the string and pass it to the context
    features = "Loading Docks,Racking Systems,Lighting and Climate Control,Climate control,Surveillance cameras,Security personnel,Restrooms and break areas,Office spaces,First aid stations".split(",")
    warehouse_facilities = warehouse.facilities.split(',')
    if request.method == 'POST':
        location_id = request.POST.get('location')
        area = request.POST.get('area')
        ownership_document = request.FILES.get('ownership_document')
        landmark = request.POST.get('landmark')
        rental_price = request.POST.get('rental_price')
        terms_cond = request.POST.get('terms_cond')
        facilities = request.POST.getlist('facilities')
        images = request.FILES.getlist('images')
        date = request.POST.get('date')
        date_obj = datetime.strptime(date, "%d %B, %Y")
        formatted_date = date_obj.strftime("%Y-%m-%d")

        if location_id and area and rental_price:
            location = Location.objects.get(pk=location_id)
            
            warehouse.location = location
            warehouse.area = area
            warehouse.ownership_documents = ownership_document
            warehouse.landmarks = landmark
            warehouse.year_built = date_obj
            warehouse.rental_price = rental_price
            warehouse.terms_cond = terms_cond
            warehouse.facilities = ','.join(facilities)
            warehouse.save()

            WarehousePhoto.objects.filter(warehouse=warehouse).delete()

            for image in images:
                WarehousePhoto.objects.create(warehouse=warehouse, image=image)

          
            return redirect('lessor_index')

    return render(request, 'warehouse/edit_warehouse.html', {'warehouse': warehouse, 'locations': locations, 'lessor_id': lessor_id, 'lessor': lessor, 'features': features, 'warehouse_facilities': warehouse_facilities})
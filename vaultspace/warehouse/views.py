# warehouse/views.py


from django.shortcuts import render,get_object_or_404
from datetime import datetime
from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from .forms import WarehouseForm, WarehousePhotoForm
from .models import Warehouse, WarehousePhoto,Location,Lease
from users.models import Lessor, Profile,User,Tenant
from users.views import lessor_index

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.utils.timezone import now
from django.utils import timezone


from decimal import Decimal

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
        
        
        if location_id and area and rental_price:
            location = Location.objects.get(pk=location_id)
            
            if lessor_id:
                lessor = Lessor.objects.get(pk=lessor_id)
                warehouse = Warehouse.objects.create(
                    owner=lessor,
                    location=location,
                    area=area,
                    ownership_documents=ownership_document,
                    landmarks=landmark,
                    year_built=date,
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
@login_required
def edit_warehouse(request, warehouse_id):
    warehouse = get_object_or_404(Warehouse, warehouse_id=warehouse_id)
    locations = Location.objects.all()
    lessor_id = request.session.get('lessor_id')
    lessor = Lessor.objects.get(lessor_id=lessor_id)
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
       

        if location_id and area and rental_price:
            location = Location.objects.get(pk=location_id)
            
            warehouse.location = location
            warehouse.area = area
            warehouse.landmarks = landmark
            warehouse.year_built = date
            warehouse.rental_price = rental_price
            warehouse.terms_cond = terms_cond
            warehouse.facilities = ','.join(facilities)

            # Handle ownership document
            if ownership_document:
                warehouse.ownership_documents = ownership_document
            else:
                warehouse.ownership_documents = request.POST.get('existing_ownership_document')

            # Handle images
            if images:
                WarehousePhoto.objects.filter(warehouse=warehouse).delete()
                for image in images:
                    WarehousePhoto.objects.create(warehouse=warehouse, image=image)
            else:
                existing_images = request.POST.getlist('existing_images')
                if existing_images:
                    WarehousePhoto.objects.filter(warehouse=warehouse).delete()
                    for image_url in existing_images:
                        WarehousePhoto.objects.create(warehouse=warehouse, image=image_url)

            warehouse.save()
            return redirect('lessor_index')

    return render(request, 'warehouse/edit_warehouse.html', {
        'warehouse': warehouse,
        'locations': locations,
        'lessor_id': lessor_id,
        'lessor': lessor,
        'features': features,
        'warehouse_facilities': warehouse_facilities
    })

##########################leasing ##########################################


@login_required
def lease_warehouse(request, warehouse_id):
    warehouse = get_object_or_404(Warehouse, warehouse_id=warehouse_id, status=1)
    tenants = Tenant.objects.all()

    if request.method == 'POST':
        print("POST data:", request.POST)
        
        tenant_id = request.POST.get('tenant_id')
        lease_start_date = request.POST.get('lease_start_date')
        lease_months = request.POST.get('lease_months')
        lease_end_date = request.POST.get('lease_end_date')
        new_monthly_rate = request.POST.get('new_monthly_rate')
        total_amount = request.POST.get('total_amount')

        print("Tenant ID:", tenant_id)
        print("Start Date:", lease_start_date)
        print("Lease Months:", lease_months)
        print("End Date:", lease_end_date)
        print("Monthly Rate:", new_monthly_rate)
        print("Total Amount:", total_amount)

        try:
            tenant = Tenant.objects.get(tenant_id=tenant_id)
            start_date = timezone.datetime.strptime(lease_start_date, "%Y-%m-%d").date()
            end_date = timezone.datetime.strptime(lease_end_date, "%Y-%m-%d").date()

            lease = Lease(
                warehouse=warehouse,
                tenant=tenant,
                lease_start_date=start_date,
                lease_end_date=end_date,
                rental_amount=Decimal(new_monthly_rate),
                total_amount=Decimal(total_amount),
                payment_status='Pending'
            )
            lease.save()
            print("Lease:", lease)
            # warehouse.status = 2  
            # # Set warehouse as not available
            # warehouse.save()

            messages.success(request,'Lease request submitted successfully!')
            return redirect('lessor_index')  # Adjust this to your actual URL name
        except Tenant.DoesNotExist:
            messages.error(request, 'Selected tenant does not exist.')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            print(f"Exception details: {e}")

    context = {
        'warehouse': warehouse,
        'tenants': tenants,
    }
    return render(request, 'warehouse/lease_warehouse.html', context)


    
@login_required
def lease_requests(request):
    # Assuming the lessor_id is stored in the session
    lessor_id = request.session.get('lessor_id')
    
    if not lessor_id:
        messages.error(request, "Lessor ID not found in session.")
        return redirect('some_error_page')  # Replace with appropriate error page

    try:
        lessor = Lessor.objects.get(lessor_id=lessor_id)
        # Get all leases for warehouses owned by this lessor
        leases = Lease.objects.filter(warehouse__owner=lessor).order_by('-lease_start_date')
        
        context = {
            'lessor': lessor,
            'leases': leases,
        }
        return render(request, 'warehouse/lease_requests.html', context)
    except Lessor.DoesNotExist:
        messages.error(request, "Lessor not found.")
        return redirect('some_error_page')  # Replace with appropriate error page

@login_required
def edit_lease(request, lease_id):
    lease = get_object_or_404(Lease, lease_id=lease_id)
    warehouse = lease.warehouse
    tenants = Tenant.objects.all()
     # Calculate the number of months between start and end date
     # Calculate the number of months between start and end date
    def months_between(d1, d2):
        return (d2.year - d1.year) * 12 + d2.month - d1.month

    lease_months = months_between(lease.lease_start_date, lease.lease_end_date)
    if lease.lease_end_date.day < lease.lease_start_date.day:
        lease_months -= 1

    print(f"Lease months: {lease_months}")

    if request.method == 'POST':
        tenant_id = request.POST.get('tenant_id')
        lease_start_date = request.POST.get('lease_start_date')
        lease_months = int(request.POST.get('lease_months'))
        lease_end_date = request.POST.get('lease_end_date')
        new_monthly_rate = float(request.POST.get('new_monthly_rate'))
        total_amount = float(request.POST.get('total_amount'))

        try:
            tenant = Tenant.objects.get(tenant_id=tenant_id)
            lease.tenant = tenant
            lease.lease_start_date = lease_start_date
            lease.lease_end_date = lease_end_date
            lease.rental_amount = new_monthly_rate
            lease.total_amount = total_amount
            lease.save()

            messages.success(request, 'Lease updated successfully!')
            return redirect('leases_requests')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')

    context = {
        'lease': lease,
        'warehouse': warehouse,
        'tenants': tenants,
        'lease_months': lease_months,
    }
    return render(request, 'warehouse/edit_lease.html', context)

@login_required
def delete_lease(request, lease_id):
    lease = get_object_or_404(Lease, lease_id=lease_id)
    if request.method == 'POST':
        lease.delete()
        messages.success(request, 'Lease deleted successfully.')
    else:
        messages.error(request, 'Invalid request method for lease deletion.')
    return redirect('lease_requests')
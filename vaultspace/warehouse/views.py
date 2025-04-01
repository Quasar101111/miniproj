# warehouse/views.py


from django.shortcuts import render,get_object_or_404
from datetime import datetime
from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from .forms import WarehouseForm, WarehousePhotoForm
from .models import Warehouse, WarehousePhoto,Location,Lease,upload_signature_path  
from users.models import Lessor, Profile,User,Tenant,Payment
from users.views import lessor_index
from map.models import Map
# from warehouse_recommender.app.price_predictor import WarehousePricePredictor

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.utils.timezone import now
from django.utils import timezone
from datetime import timedelta


from django.db.models import Count,Sum,F
from django.db.models.functions import TruncMonth



from django.http import JsonResponse

import os
import json
from decimal import Decimal

from blockchain.service import BlockchainService
from web3 import Web3

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from ai.service import GeminiService
import uuid
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings


@login_required
def add_warehouse(request):
    lessor_id = request.session.get('lessor_id')
    lessor = Lessor.objects.get(lessor_id=lessor_id)
    today = now().date()

    if request.method == 'POST':
        # Get location data from the form
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        area = request.POST.get('area')
        ownership_document = request.FILES.get('ownership_document')
        landmark = request.POST.get('landmark')
        rental_price = request.POST.get('rental_price')
        terms_cond = request.POST.get('terms_cond')
        facilities = request.POST.getlist('facilities')
        images = request.FILES.getlist('images')
        date = request.POST.get('date')
        length = request.POST.get('length')
        breadth = request.POST.get('breadth')
        height = request.POST.get('height')
        
        # Check for files uploaded via chat
        chat_uploaded_files = request.session.get('uploaded_files', {})
        
        # Get ownership document from chat uploads if not provided in form
        if not ownership_document and 'ownership_document' in chat_uploaded_files:
            # Get the saved path
            doc_path = chat_uploaded_files['ownership_document']
            # Create a file object from the saved file
            ownership_document = default_storage.open(doc_path)
            print(f"Using ownership document uploaded via chat: {doc_path}")
        
        # Get images from chat uploads and combine with form uploads
        chat_images = []
        if 'images' in chat_uploaded_files and chat_uploaded_files['images']:
            for img_path in chat_uploaded_files['images']:
                chat_images.append(default_storage.open(img_path))
                print(f"Using image uploaded via chat: {img_path}")
        
        # Combine images from both sources
        all_images = list(images) + chat_images
        
        print("Latitude:", latitude)
        print("Longitude:", longitude)

        if latitude and longitude and area and rental_price:
            try:
                # Create the warehouse first
                warehouse = Warehouse.objects.create(
                    owner=lessor,
                    area=area,
                    ownership_documents=ownership_document,
                    landmarks=landmark,
                    year_built=date,
                    rental_price=rental_price,
                    terms_cond=terms_cond,
                    facilities=','.join(facilities),
                    status=1,
                    length=length,
                    breadth=breadth,
                    height=height,
                )

                # Create the map entry with the warehouse reference
                Map.objects.create(
                    warehouse=warehouse,
                    latitude=latitude,
                    longitude=longitude
                )

                # Store in blockchain
                try:
                    service = BlockchainService()
                    location_string = f"{latitude},{longitude}"
                    
                    # Get current gas price and nonce
                    current_gas_price = service.w3.eth.gas_price
                    if current_gas_price == 0:
                        raise ValueError("Invalid gas price received from network")
                    
                    wallet_address = os.getenv('WALLET_ADDRESS')
                    nonce = service.w3.eth.get_transaction_count(wallet_address)

                    # Build transaction with proper gas parameters
                    tx = service.contract.functions.addWarehouse(
                        str(warehouse.warehouse_id),
                        location_string,
                        int(float(area)),
                        int(float(rental_price))
                    ).build_transaction({
                        'chainId': 11155111,  # Sepolia chain ID
                        'from': wallet_address,
                        'nonce': nonce,
                        'gas': 2000000,  # Fixed gas limit
                        'maxFeePerGas': int(current_gas_price * 2),
                        'maxPriorityFeePerGas': int(current_gas_price * 1.5),
                    })

                    # Sign and send transaction
                    signed_tx = service.w3.eth.account.sign_transaction(
                        tx, 
                        private_key=os.getenv('PRIVATE_KEY')
                    )
                    tx_hash = service.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                    
                    # Wait for receipt with longer timeout
                    receipt = service.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
                    warehouse.blockchain_tx = tx_hash.hex()
                    warehouse.save()
                    
                    if receipt.status != 1:
                        messages.warning(request, 'Warehouse saved but blockchain storage failed')
                    else:
                        messages.success(request, 'Warehouse saved successfully including blockchain storage')
                    
                except Exception as e:
                    messages.warning(request, f'Warehouse saved but blockchain storage failed: {str(e)}')

                # Save warehouse photos
                for image in all_images:
                    WarehousePhoto.objects.create(warehouse=warehouse, image=image)

                # Clear the uploaded files from the session
                if 'uploaded_files' in request.session:
                    del request.session['uploaded_files']
                    request.session.modified = True

                return redirect('lessor_index')
            except Exception as e:
                messages.error(request, f'Error saving warehouse: {str(e)}')
        else:
            messages.error(request, 'Please fill in all required fields')

    return render(request, 'warehouse/add_warehouse.html', {
        'lessor_id': lessor_id,
        'lessor': lessor,
        'today': today
    })

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
        length = request.POST.get('length')
        breadth = request.POST.get('breadth')
        height = request.POST.get('height')
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

import requests
@login_required
def lease_warehouse(request, warehouse_id):
    warehouse = get_object_or_404(Warehouse, warehouse_id=warehouse_id, status=1)
    tenants = Tenant.objects.all()
    lessor = warehouse.owner
    lessor_id = lessor.lessor_id
    
    # Initialize price_suggestions with default values
    price_suggestions = {
        'optimal_price': float(warehouse.rental_price),
        'price_range': {
            'low': float(warehouse.rental_price) * 0.8,
            'high': float(warehouse.rental_price) * 1.2
        },
        'price_per_sqft': float(warehouse.rental_price) / float(warehouse.area),
        'confidence': 0.0,
        'current_price': float(warehouse.rental_price)
    }
    
    try:
        import requests
        api_url = f"{settings.RECOMMENDER_API_URL}/predict/price"
        
        # Get location from Map model if location field is None
        if warehouse.location is None:
            map_location = Map.objects.filter(warehouse=warehouse).first()
            if map_location:
                latitude = map_location.latitude
                longitude = map_location.longitude
            else:
                raise ValueError("Warehouse location not found")
        else:
            latitude = warehouse.location.latitude
            longitude = warehouse.location.longitude
        
        # Convert Decimal to float for JSON serialization
        area = float(warehouse.area)
        
        # Use actual warehouse data
        payload = {
            "area": area,
            "latitude": float(latitude),
            "longitude": float(longitude)
        }
        
        print("Sending request to FastAPI service...")
        print("Request data:", json.dumps(payload, indent=2))
        print("API URL:", api_url)
        
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        price_data = response.json()
        
        print("Received response from FastAPI service:")
        print(json.dumps(price_data, indent=2))
        
        # Update price_suggestions with actual data
        price_suggestions.update({
            'optimal_price': round(float(price_data['optimal_price']), 2),
            'price_range': {
                'low': round(float(price_data['price_range']['low']), 2),
                'high': round(float(price_data['price_range']['high']), 2)
            },
            'price_per_sqft': round(float(price_data['price_per_sqft']), 2),
            'confidence': round(float(price_data['confidence']), 1)
        })
        
        print("\nPrice Prediction Results:")
        print(f"Optimal Price: ₹{price_suggestions['optimal_price']:,.2f}")
        print(f"Price Range: ₹{price_suggestions['price_range']['low']:,.2f} - ₹{price_suggestions['price_range']['high']:,.2f}")
        print(f"Price per sqft: ₹{price_suggestions['price_per_sqft']:,.2f}")
        print(f"Confidence Level: {price_suggestions['confidence']:.1f}%")
        
    except requests.exceptions.RequestException as e:
        print(f"FastAPI request error: {str(e)}")
        messages.warning(request, f'Could not fetch price suggestions: {str(e)}')
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        messages.warning(request, f'An unexpected error occurred: {str(e)}')
    
    if request.method == 'POST':
        print("POST data:", request.POST)
        
        tenant_id = request.POST.get('tenant_id')
        lease_start_date = request.POST.get('lease_start_date')
        lease_months = request.POST.get('lease_months')
        lease_end_date = request.POST.get('lease_end_date')
        new_monthly_rate = request.POST.get('new_monthly_rate')
        total_amount = request.POST.get('total_amount')
        signature = request.FILES.get('signature')

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
                payment_status='Pending',
                lessor_signature = signature
            )
            
            lease.save()
            print("Lease:", lease)

            messages.success(request,'Lease request submitted successfully!')
            return redirect('lessor_index')
        except Tenant.DoesNotExist:
            messages.error(request, 'Selected tenant does not exist.')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            print(f"Exception details: {e}")

    context = {
        'warehouse': warehouse,
        'tenants': tenants,
        'lessor': lessor,
        'price_suggestions': price_suggestions
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

def termsandcond(request):
    return render(request,'termsandcond')



@login_required
def lessor_dashboard(request):
    lessor = Lessor.objects.get(email=request.user.email)
    warehouses = Warehouse.objects.filter(owner=lessor)
    
    # Calculate key metrics
    total_warehouses = warehouses.count()
    occupied_warehouses = warehouses.filter(status=2).count()  # Assuming status 2 means occupied
    available_warehouses = total_warehouses - occupied_warehouses
    
    # Get active leases
    active_leases = Lease.objects.filter(warehouse__in=warehouses, lease_end_date__gte=timezone.now())
    print(active_leases)
    # Calculate total revenue
    total_revenue = active_leases.aggregate(Sum('rental_amount'))['rental_amount__sum'] or 0
    
    # Get revenue by location
    revenue_by_location = Location.objects.filter(warehouse__in=warehouses).annotate(
        revenue=Sum('warehouse__lease__rental_amount')
    ).values('city', 'state', 'revenue').order_by('-revenue')
    
    # Get recent leases
    recent_leases = active_leases.order_by('-lease_start_date')
    
    revenue_data = []
    for warehouse in warehouses:
        warehouse_leases = active_leases.filter(warehouse=warehouse)
        monthly_revenue = warehouse_leases.annotate(
            month=TruncMonth('lease_start_date')
        ).values('month').annotate(
            revenue=Sum('rental_amount')
        ).order_by('month')
        
        warehouse_data = [
            [int(datetime(item['month'].year, item['month'].month, 1).timestamp() * 1000), float(item['revenue'])]
            for item in monthly_revenue
        ]
        
        revenue_data.append({
            'name': warehouse.name,
            'data': warehouse_data
        })
         # Prepare data for chart
    revenue_by_warehouse = []

    for warehouse in warehouses:
        leases = Lease.objects.filter(warehouse=warehouse)

        # Create a list of data points (date and revenue) for each lease
        warehouse_revenue_data = []
        for lease in leases:
            start_date = lease.lease_start_date
            end_date = lease.lease_end_date
            revenue = lease.rental_amount

            # Add start and end date with revenue to the data
            warehouse_revenue_data.append({
                'start_date': start_date,
                'end_date': end_date,
                'revenue': revenue
            })

        revenue_by_warehouse.append({
            'name': warehouse.name,
            'data': warehouse_revenue_data
        })
 

    context = {
        'total_warehouses': total_warehouses,
        'occupied_warehouses': occupied_warehouses,
        'available_warehouses': available_warehouses,
        'total_revenue': total_revenue,
        'revenue_by_location': revenue_by_location,
        'recent_leases': recent_leases,
        'warehouses': warehouses,
        'revenue_data': json.dumps(revenue_data),  # Convert to JSON for JavaScript
        'revenue_by_warehouse': revenue_by_warehouse,
    }
    return render(request, 'warehouse/dashboard.html', context)

@login_required
def revenue_chart_data(request):
    lessor = Lessor.objects.get(email=request.user.email)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)  # Last 12 months

    revenue_data = Lease.objects.filter(
        warehouse__owner=lessor,
        lease_start_date__gte=start_date,
        lease_start_date__lte=end_date
    ).annotate(
        month=TruncMonth('lease_start_date')
    ).values('month').annotate(
        revenue=Sum('rental_amount')
    ).order_by('month')

    labels = []
    data = []

    for entry in revenue_data:
        labels.append(entry['month'].strftime('%b %Y'))
        data.append(float(entry['revenue']))

    return JsonResponse({
        'labels': labels,
        'data': data
    })

@login_required
def warehouse_status_chart_data(request):
    lessor = Lessor.objects.get(email=request.user.email)
    warehouses = Warehouse.objects.filter(owner=lessor)
    
    occupied = warehouses.filter(status=2).count()  # Assuming status 2 means occupied
    available = warehouses.count() - occupied

    return JsonResponse({
        'labels': ['Occupied', 'Available'],
        'data': [occupied, available]
    })



@login_required
def compare_warehouse(request):
    # Fetch all warehouses with their photos
    warehouses = Warehouse.objects.prefetch_related('photos').all()

    # Prepare the context with the warehouse data
    context = {
        'warehouses': warehouses,
    }
    
    return render(request, 'warehouse/compare_warehouse.html', context)



def trending_warehouses(request):
    trending = Warehouse.objects.filter(status=1).order_by('-popularity_score')[:10]
    return JsonResponse({
        'trending': [
            {
                'id': wh.warehouse_id,
                'name': wh.name,
                'price': float(wh.rental_price),
                'popularity': wh.popularity_score,
                'photo': wh.photos.first().image.url if wh.photos.exists() else None
            } 
            for wh in trending
        ]
    })

def manage_availability(request):
    if request.method == "POST":
        form = WarehouseAvailabilityForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('warehouse_availability')
    else:
        form = WarehouseAvailabilityForm()
    
    availabilities = WarehouseAvailability.objects.all()
    return render(request, 'warehouse_availability.html', {'form': form, 'availabilities': availabilities})

@login_required
def tenant_availability_calendar(request):
    # Fetch all warehouses and their availability/lease data
    warehouses = Warehouse.objects.all()
    return render(request, 'warehouse/tenant_availability_calendar.html', {'warehouses': warehouses})


@login_required
def tenant_availability_api(request):
    # Fetch all warehouses
    warehouses = Warehouse.objects.all()
    events = []

    # Add warehouse availability events
    for warehouse in warehouses:
        # Get all leases for this warehouse
        warehouse_leases = leases.filter(warehouse=warehouse).order_by('lease_start_date')

        # Initialize availability start date (e.g., today or a fixed date)
        availability_start = timezone.now().date()

        # Iterate through leases to calculate availability periods
        for lease in warehouse_leases:
            # If the lease starts after the current availability period, there's a gap
            if lease.lease_start_date > availability_start:
                events.append({
                    "title": f"{warehouse.name} - Available",
                    "start": str(availability_start),
                    "end": str(lease.lease_start_date - timedelta(days=1)),  # End before lease starts
                    "backgroundColor": "#4CAF50"  # Green for available
                })

            # Update the availability start date to after the lease ends
            availability_start = lease.lease_end_date + timedelta(days=1)

        # Add the final availability period (after the last lease)
        events.append({
            "title": f"{warehouse.warehouse_id} - Available",
            "start": str(availability_start),
            "end": str(availability_start + timedelta(days=365)),  # Arbitrary end date (e.g., 1 year later)
            "backgroundColor": "#4CAF50"  # Green for available
        })

    # Add lease events
    for lease in leases:
        events.append({
            "title": f"{lease.warehouse.warehouse_id} - Leased to {lease.tenant.tenant_name}",
            "start": str(lease.lease_start_date),
            "end": str(lease.lease_end_date),
            "backgroundColor": "#ff4d4d"  # Red for leased
        })

    # Print the events data for debugging
    print("Events data being passed to the calendar:", events)

    return JsonResponse(events, safe=False)



@require_POST
def process_warehouse_chat(request):
    """Process warehouse chat messages and extract warehouse details."""
    try:
        message = request.POST.get('message', '')
        print(f"Received message: '{message}'")
        
        if not message:
            return JsonResponse({
                'message': 'Please type a message about your warehouse.',
                'data': None,
                'type': 'error'
            })
        
        # Initialize the Gemini service
        gemini_service = GeminiService()
        
        # Process the message and get response
        result = gemini_service.parse_warehouse_details(message)
        print(f"AI service result: {result}")
        
        # Check if the result is a dictionary containing a message (error case)
        if isinstance(result, dict) and 'message' in result:
            return JsonResponse({
                'message': result['message'],
                'data': None,
                'type': 'error'
            })
        
        # Normal case - we have warehouse details
        if isinstance(result, dict):
            # Clean up the data to ensure proper types
            if result.get('length'):
                result['length'] = float(result['length']) if result['length'] is not None else None
            if result.get('breadth'):
                result['breadth'] = float(result['breadth']) if result['breadth'] is not None else None
            if result.get('height'):
                result['height'] = float(result['height']) if result['height'] is not None else None
            if result.get('rental_price'):
                # Remove currency symbol and convert to number
                if isinstance(result['rental_price'], str):
                    price_str = result['rental_price'].replace('₹', '').replace(',', '')
                    result['rental_price'] = float(price_str)
            
            # Fix landmarks/landmark field
            if result.get('landmarks') and not result.get('landmark'):
                result['landmark'] = result.pop('landmarks')
            
            # Construct a nice response message
            response_parts = []
            
            # Create a more natural response when the user provides information
            if result.get('length') or result.get('breadth') or result.get('height'):
                dimensions = []
                if result.get('length'):
                    dimensions.append(f"{result['length']} feet long")
                if result.get('breadth'):
                    dimensions.append(f"{result['breadth']} feet wide")
                if result.get('height'):
                    dimensions.append(f"{result['height']} feet high")
                
                if len(dimensions) == 1:
                    response_parts.append(f"I see your warehouse is {dimensions[0]}.")
                elif len(dimensions) == 2:
                    response_parts.append(f"I see your warehouse is {dimensions[0]} and {dimensions[1]}.")
                else:
                    response_parts.append(f"I see your warehouse is {', '.join(dimensions[:-1])}, and {dimensions[-1]}.")
            
            if result.get('landmark'):
                response_parts.append(f"It's located near {result['landmark']}.")
            
            if result.get('rental_price'):
                response_parts.append(f"You're offering it for rent at ₹{result['rental_price']} per month.")
            
            if result.get('facilities') and len(result['facilities']) > 0:
                if len(result['facilities']) == 1:
                    response_parts.append(f"It has {result['facilities'][0]}.")
                elif len(result['facilities']) == 2:
                    response_parts.append(f"It has {result['facilities'][0]} and {result['facilities'][1]}.")
                else:
                    response_parts.append(f"It has {', '.join(result['facilities'][:-1])}, and {result['facilities'][-1]}.")
            
            response_message = " ".join(response_parts)
            
            # If we have details to confirm
            if response_parts:
                response_message += " I've updated your form with these details."
                
                # Add contextual follow-up questions based on missing fields
                follow_ups = []
                if (result.get('length') is None or result.get('breadth') is None or result.get('height') is None):
                    missing_dimensions = []
                    if result.get('length') is None:
                        missing_dimensions.append("length")
                    if result.get('breadth') is None:
                        missing_dimensions.append("width")
                    if result.get('height') is None:
                        missing_dimensions.append("height")
                    
                    if missing_dimensions:
                        dimension_text = " and ".join(missing_dimensions)
                        follow_ups.append(f"Could you also tell me the {dimension_text} of your warehouse?")
                
                if result.get('landmark') is None:
                    follow_ups.append("Where is your warehouse located?")
                
                if result.get('rental_price') is None:
                    follow_ups.append("How much are you planning to rent it for?")
                
                if not result.get('facilities') or len(result['facilities']) == 0:
                    follow_ups.append("What facilities does your warehouse offer?")
                
                # Add a maximum of 2 follow-up questions to keep it conversational
                if follow_ups:
                    if len(follow_ups) == 1:
                        response_message += f" {follow_ups[0]}"
                    else:
                        response_message += f" {follow_ups[0]} {follow_ups[1]}"
            else:
                # If we couldn't extract any details
                response_message = "I'd like to help you with your warehouse details. Could you tell me more about it? For example, you could describe its size, location, facilities, or rental price."
            
            # Return the formatted response
            print(f"Returning processed data: {result}")
            return JsonResponse({
                'message': response_message,
                'data': result,
                'type': 'warehouse_details'
            })
        
        # Fallback response if no valid result
        return JsonResponse({
            'message': "I'm having trouble understanding that. Could you try describing your warehouse in a different way? For example, you could tell me about its size, location, or what facilities it has.",
            'data': None,
            'type': 'error'
        })
        
    except Exception as e:
        import traceback
        print(f"Error processing warehouse chat: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({
            'message': "I'm having a bit of trouble processing that. Could you try breaking it down into smaller pieces? For example, you could start by telling me about the warehouse's size, then its location, and finally what facilities it offers.",
            'data': None,
            'type': 'error'
        })

@require_POST
def process_warehouse_files(request):
    """Process file uploads from the warehouse chat interface."""
    try:
        files = request.FILES.getlist('files[]')
        print(f"Received {len(files)} files")
        
        if not files:
            return JsonResponse({
                'message': 'No files were uploaded.',
                'files': []
            })
        
        processed_files = []
        
        for file in files:
            original_name = file.name
            file_extension = os.path.splitext(original_name)[1].lower()
            
            # Generate a unique filename
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Determine file type based on extension
            file_type = 'image' if file_extension in ['.jpg', '.jpeg', '.png'] else 'ownership_document'
            
            # Determine the appropriate path
            if file_type == 'image':
                path = f'warehouse_photos/{unique_filename}'
            else:
                path = f'ownership_documents/{unique_filename}'
            
            # Save the file to the appropriate location
            saved_path = default_storage.save(path, ContentFile(file.read()))
            
            # Add to processed files
            processed_files.append({
                'name': original_name,
                'saved_as': saved_path,
                'type': file_type,
                'size': file.size
            })
            
            print(f"Saved file {original_name} as {saved_path}")
        
        # Create a descriptive message
        image_count = sum(1 for f in processed_files if f['type'] == 'image')
        doc_count = sum(1 for f in processed_files if f['type'] == 'ownership_document')
        
        message_parts = []
        
        if image_count > 0:
            message_parts.append(f"{image_count} warehouse image{'s' if image_count > 1 else ''}")
        
        if doc_count > 0:
            message_parts.append(f"{doc_count} ownership document{'s' if doc_count > 1 else ''}")
        
        message = f"I've received {' and '.join(message_parts)}. "
        
        if image_count > 0:
            message += "The images will be used for your warehouse listing. "
        
        if doc_count > 0:
            message += "The ownership document will be used to verify your ownership of the warehouse."
        
        # Store the file paths in the session to access them when the form is submitted
        if 'uploaded_files' not in request.session:
            request.session['uploaded_files'] = {}
        
        for file in processed_files:
            if file['type'] == 'image':
                if 'images' not in request.session['uploaded_files']:
                    request.session['uploaded_files']['images'] = []
                request.session['uploaded_files']['images'].append(file['saved_as'])
            else:
                request.session['uploaded_files']['ownership_document'] = file['saved_as']
        
        request.session.modified = True
        
        return JsonResponse({
            'message': message,
            'files': processed_files
        })
        
    except Exception as e:
        import traceback
        print(f"Error processing file uploads: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({
            'message': f"There was an error processing your files: {str(e)}",
            'files': []
        }, status=500)

@login_required
def verify_warehouse_blockchain(request, warehouse_id):
    """
    View to compare warehouse details in the database with blockchain and display the results
    """
    warehouse = get_object_or_404(Warehouse, warehouse_id=warehouse_id)
    
    # Initialize dictionaries to store comparison data
    blockchain_data = {}
    database_data = {}
    comparison_results = {}
    verification_error = None
    
    if warehouse.blockchain_tx:
        try:
            # Fetch location from Map model if location field is None
            if warehouse.location is None:
                map_location = Map.objects.filter(warehouse=warehouse).first()
                if map_location:
                    local_location = f"{map_location.latitude},{map_location.longitude}"
                else:
                    raise ValueError("Warehouse location is not set in either Location or Map model")
            else:
                local_location = f"{warehouse.location.latitude},{warehouse.location.longitude}"
            
            service = BlockchainService()
            # Fetch warehouse data from blockchain
            bc_data = service.contract.functions.getWarehouse(warehouse.warehouse_id).call()
            
            # Prepare local data for comparison
            local_area = int(float(warehouse.area))
            local_rental_price = int(float(warehouse.rental_price))
            
            # Store blockchain data in dictionary
            blockchain_data = {
                'id': bc_data[0],
                'name': bc_data[1],
                'location': bc_data[2],
                'area': bc_data[3],
                'rental_price': bc_data[4],
                'owner': bc_data[5]
            }
            
            # Store database data in dictionary
            database_data = {
                'id': warehouse.warehouse_id,
                'name': warehouse.name,
                'location': local_location,
                'area': local_area,
                'rental_price': local_rental_price,
                'owner': warehouse.owner.wallet_address if hasattr(warehouse.owner, 'wallet_address') else None
            }
            
            # Compare fields and store results
            all_match = True
            for field in blockchain_data:
                field_match = blockchain_data[field] == database_data[field]
                comparison_results[field] = {
                    'blockchain': blockchain_data[field],
                    'database': database_data[field],
                    'match': field_match
                }
                if not field_match:
                    all_match = False
                    
        except Exception as e:
            import traceback
            verification_error = str(e)
            print(f"Blockchain Verification Error: {str(e)}")
            print(traceback.format_exc())
    else:
        verification_error = "This warehouse has not been stored on the blockchain"
        
    return render(request, 'warehouse/verify_blockchain.html', {
        'warehouse': warehouse,
        'blockchain_data': blockchain_data,
        'database_data': database_data,
        'comparison_results': comparison_results,
        'all_fields_match': all_match if 'all_match' in locals() else False,
        'verification_error': verification_error
    })

@login_required
def sync_blockchain_data(request, warehouse_id):
    """
    View to sync warehouse data in the blockchain if it's out of sync with the database
    """
    warehouse = get_object_or_404(Warehouse, warehouse_id=warehouse_id)
    sync_result = {'status': 'error', 'message': 'No action taken'}
    
    if request.method == 'POST':
        try:
            # Get the map location
            if warehouse.location is None:
                map_location = Map.objects.filter(warehouse=warehouse).first()
                if map_location:
                    location_string = f"{map_location.latitude},{map_location.longitude}"
                else:
                    raise ValueError("Warehouse location is not set in either Location or Map model")
            else:
                location_string = f"{warehouse.location.latitude},{warehouse.location.longitude}"
                
            service = BlockchainService()
            
            # Get current gas price and nonce
            current_gas_price = service.w3.eth.gas_price
            if current_gas_price == 0:
                raise ValueError("Invalid gas price received from network")
            
            wallet_address = os.getenv('WALLET_ADDRESS')
            nonce = service.w3.eth.get_transaction_count(wallet_address)
            
            # Prepare transaction to update warehouse data
            tx = service.contract.functions.addWarehouse(
                str(warehouse.warehouse_id),
                location_string,
                int(float(warehouse.area)),
                int(float(warehouse.rental_price))
            ).build_transaction({
                'chainId': 11155111,  # Sepolia chain ID
                'from': wallet_address,
                'nonce': nonce,
                'gas': 2000000,  # Fixed gas limit
                'maxFeePerGas': int(current_gas_price * 2),
                'maxPriorityFeePerGas': int(current_gas_price * 1.5),
            })
            
            # Sign and send transaction
            signed_tx = service.w3.eth.account.sign_transaction(
                tx, 
                private_key=os.getenv('PRIVATE_KEY')
            )
            tx_hash = service.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            # Wait for receipt
            receipt = service.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            # Update warehouse blockchain_tx field
            warehouse.blockchain_tx = tx_hash.hex()
            warehouse.save()
            
            if receipt.status == 1:
                sync_result = {
                    'status': 'success',
                    'message': 'Warehouse data successfully synchronized with blockchain',
                    'tx_hash': tx_hash.hex()
                }
                messages.success(request, 'Warehouse data successfully synchronized with blockchain')
            else:
                sync_result = {
                    'status': 'error',
                    'message': 'Transaction completed but may have failed. Please verify the data again.',
                    'tx_hash': tx_hash.hex()
                }
                messages.warning(request, 'Transaction completed but may have failed. Please verify the data again.')
                
        except Exception as e:
            sync_result = {'status': 'error', 'message': str(e)}
            messages.error(request, f'Error synchronizing with blockchain: {str(e)}')
    
    # Redirect to the verification page
    return redirect('verify_warehouse_blockchain', warehouse_id=warehouse_id)

@login_required
def get_blockchain_details(request, warehouse_id):
    """
    View to fetch and display the raw blockchain data for a warehouse
    """
    warehouse = get_object_or_404(Warehouse, warehouse_id=warehouse_id)
    blockchain_data = {}
    fetch_error = None
    
    if warehouse.blockchain_tx:
        try:
            service = BlockchainService()
            # Fetch warehouse data from blockchain
            bc_data = service.contract.functions.getWarehouse(warehouse.warehouse_id).call()
            
            # Store blockchain data in dictionary
            blockchain_data = {
                'id': bc_data[0],
                'name': bc_data[1],
                'location': bc_data[2],
                'area': bc_data[3],
                'rental_price': bc_data[4],
                'owner': bc_data[5]
            }
            
        except Exception as e:
            import traceback
            fetch_error = str(e)
            print(f"Blockchain Fetch Error: {str(e)}")
            print(traceback.format_exc())
    else:
        fetch_error = "This warehouse has not been stored on the blockchain"
    
    return render(request, 'warehouse/blockchain_details.html', {
        'warehouse': warehouse,
        'blockchain_data': blockchain_data,
        'fetch_error': fetch_error
    })

@login_required
def get_optimal_lease_price(request, warehouse_id):
    """Get optimal lease price suggestions for a warehouse"""
    try:
        warehouse = get_object_or_404(Warehouse, warehouse_id=warehouse_id)
        
        # Get location from Map model if location field is None
        if warehouse.location is None:
            map_location = Map.objects.filter(warehouse=warehouse).first()
            if map_location:
                latitude = map_location.latitude
                longitude = map_location.longitude
            else:
                return JsonResponse({
                    'error': 'Warehouse location not found'
                }, status=400)
        else:
            latitude = warehouse.location.latitude
            longitude = warehouse.location.longitude
        
        # Make request to FastAPI service
        import requests
        api_url = "http://127.0.0.1:8001/predict/price"
        payload = {
            "area": float(warehouse.area),
            "latitude": latitude,
            "longitude": longitude
        }
        
        response = requests.post(api_url, json=payload)
        if response.status_code != 200:
            return JsonResponse({
                'error': f'Error from recommender service: {response.text}'
            }, status=response.status_code)
            
        suggestions = response.json()
        
        # Format the response
        response_data = {
            'warehouse_id': warehouse.warehouse_id,
            'area': warehouse.area,
            'location': f"{warehouse.location.city}, {warehouse.location.state}" if warehouse.location else "Location not specified",
            'suggestions': {
                'optimal_price': round(suggestions['optimal_price'], 2),
                'price_range': {
                    'low': round(suggestions['price_range']['low'], 2),
                    'high': round(suggestions['price_range']['high'], 2)
                },
                'price_per_sqft': round(suggestions['price_per_sqft'], 2),
                'confidence': round(suggestions['confidence'], 1)
            },
            'current_price': float(warehouse.rental_price)
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
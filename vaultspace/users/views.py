#users/views.py
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout,get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError

from django.db.models import F
from .forms import LessorRegisterForm,TenantRegisterForm,CustomAuthenticationForm
from .forms import LessorForm,TenantForm,WarehouseReviewForm

from .models import Profile,Lessor,User,UnverifiedUser,Tenant,Message,Payment
from warehouse.models import Location,Warehouse,WarehousePhoto,Lease,WarehouseReview

from django.db.models import Q, Max
from django.core.files.base import ContentFile



from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string


from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import Paginator
from django.utils import timezone
from django.shortcuts import redirect
from django.template.loader import get_template


from django.contrib.auth.decorators import user_passes_test
import random
import string
import io,os,uuid,tempfile 
from django.core.files.storage import default_storage


from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy

import razorpay

import pdfkit

from django.http import HttpResponse
from django.template.loader import get_template
from wkhtmltopdf.views import PDFTemplateView

from django.utils.decorators import method_decorator

from .utils.image_processing import generate_shares, save_image_with_hash,  calculate_hash,get_hash_from_image
from .utils.sort_warehosue import sort_warehouses


from django.core.files.base import ContentFile
from .models import ServerShare

from django.core.files.base import ContentFile
from PIL import Image, PngImagePlugin 
import numpy as np 
import hashlib

#################### index####################################### 

def index(request):
  
   
    locations = Location.objects.all()
    
    warehouses = Warehouse.objects.prefetch_related('photos').all().order_by('-warehouse_id')
    context = {
        'warehouses': warehouses,
        'locations': locations,
    }
    return render(request, 'users/index.html', context)

########### register here ##################################### 
def temp(request):
   
    
   
    locations = Location.objects.all()
    
    warehouses = Warehouse.objects.prefetch_related('photos').all().order_by('-warehouse_id')
    context = {
        'warehouses': warehouses,
        'locations': locations,
    }
    return render(request, 'users/temp.html', context)

def register_tenant(request):
    if request.method == 'POST':
        form = TenantRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                existing_user = User.objects.get(email=email)
                messages.error(request, 'A user with this email already exists.')
                return render(request, 'users/register_tenant.html', {'form': form})
            except User.DoesNotExist:
                # Generate and send OTP
                otp = generate_otp()
                request.session['registration_data'] = form.cleaned_data
                request.session['otp'] = otp
                request.session['user_type'] = 'tenant'
                request.session['email']= email
                
                send_mail(
                    'Verify your email',
                    f'Your OTP is: {otp}',
                    'vaultspace07@gmail.com',
                    [email],
                    fail_silently=False,
                )

                messages.success(request, 'Please check your email for OTP verification.')
                return render(request, 'users/register_tenant.html', {'show_otp_form': True})
        
    else:
        form = TenantRegisterForm()
    
    return render(request, 'users/register_tenant.html', {'form': form})

          

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def register_lessor(request):
    if request.method == 'POST':
        form = LessorRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                existing_user = User.objects.get(email=email)
                messages.error(request, 'A user with this email already exists.')
                return render(request, 'users/register_lessor.html', {'form': form})
            except User.DoesNotExist:
                # Generate and send OTP
                otp = generate_otp()
                request.session['registration_data'] = form.cleaned_data
                request.session['otp'] = otp
                request.session['user_type'] = 'lessor'
                request.session['email']= email
                
                send_mail(
                    'Verify your email',
                    f'Your OTP is: {otp}',
                    'vaultspace07@gmail.com',
                    [email],
                    fail_silently=False,
                )

                messages.success(request, 'Please check your email for OTP verification.')
                return render(request, 'users/register_lessor.html', {'show_otp_form': True})
        
    else:
        form = LessorRegisterForm()
    
    return render(request, 'users/register_lessor.html', {'form': form})

def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        registration_data = request.session.get('registration_data')
        user_type = request.session.get('user_type')

        if otp == stored_otp and registration_data:
            # Create user and profile
            user = User.objects.create_user(
                username=registration_data['email'],
                email=registration_data['email'],
                password=registration_data['password1']
            )
            profile = Profile.objects.create(user=user, user_type=user_type)

           

            # Clear session data
            del request.session['registration_data']
            del request.session['otp']
            del request.session['user_type']

            messages.success(request, 'Registration successful! You can now log in.')

            return redirect('upload_image_share')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            if user_type == 'tenant':
                return render(request, 'users/register_tenant.html', {'show_otp_form': True})
            else:
                return render(request, 'users/register_lessor.html', {'show_otp_form': True})

    return redirect('register_tenant' if request.session.get('user_type') == 'tenant' else 'register_lessor')
   

def verify_otp2(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        registration_data = request.session.get('registration_data')
        user_type = request.session.get('user_type')

        if otp == stored_otp and registration_data:
            # Create user and profile
            user = User.objects.create_user(
                username=registration_data['email'],
                email=registration_data['email'],
                password=registration_data['password1']
            )
            profile = Profile.objects.create(user=user, user_type=user_type)

            # Clear session data
            del request.session['registration_data']
            del request.session['otp']

            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            return render(request, 'users/register_tenat.html', {'show_otp_form': True})

    return redirect('register_tenant')



   

################ user details################################################### 

@login_required(login_url='login')
def lessor_details(request):
    try:
        # Fetch the Lessor instance associated with the logged-in user's email
        lessor = Lessor.objects.get(email=request.user.email)
        context = {
        'title': 'temp',
        'lessor': lessor
    }
    except Lessor.DoesNotExist:
        lessor = None

    if request.method == 'POST':
        form = LessorForm(request.POST, request.FILES, instance=lessor)
        if form.is_valid():
            lessor = form.save(commit=False)
            lessor.email = request.user.email  # Set email to the logged-in user's email
            lessor.save()
            
            return redirect('lessor_index')

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        if lessor:
            form = LessorForm(instance=lessor)
            
        else:
            form = LessorForm(initial={'email': request.user.email})

    return render(request, 'users/lessor_details.html', {'form': form, 'title': 'Lessor Registration', 'lessor': lessor})


@login_required
def tenant_details(request):
    try:
        # Fetch the Lessor instance associated with the logged-in user's email
        tenant = Tenant.objects.get(email=request.user.email)
        context = {
        'title': 'temp',
        'tenant': tenant
    }
    except Tenant.DoesNotExist:
        tenant = None

    if request.method == 'POST':
        form = TenantForm(request.POST, request.FILES, instance=tenant)
        if form.is_valid():
            tenant = form.save(commit=False)
            tenant.email = request.user.email  # Set email to the logged-in user's email
            tenant.save()
            messages.success(request, 'Tenant details have been saved successfully!')
            return redirect('index')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        if tenant:
            form = TenantForm(instance=tenant)
            
        else:
            form = TenantForm(initial={'email': request.user.email})

    return render(request, 'users/tenant_details.html', {'form': form, 'title': 'Tenant Registration', 'tenant': tenant})
################ login forms################################################### from django.shortcuts import render, redirect

def Login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, request.POST)
        
        if form.is_valid():
            email = form.cleaned_data.get('username')  # here username=email from forms
            password = form.cleaned_data.get('password')
            
            # Validate email format
            email_validator = EmailValidator()
            try:
                email_validator(email)
            except ValidationError:
                messages.error(request, 'Invalid email format.')
                return render(request, 'users/login.html', {'form': form, 'title': 'log in'})
            
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                
                if user.is_superuser:
                    return redirect('admin_dashboard')  # Redirect superuser to admin dashboard
                
                try:
                    profile = Profile.objects.get(user=user)
                    if profile.user_type == 'tenant':
                        try:
                            tenant = Tenant.objects.get(email=user.email)
                            request.session['tenant_id'] = tenant.tenant_id
                            request.session.save()
                            return redirect('index')
                        except Tenant.DoesNotExist:
                            return redirect('tenant_details')
                    elif profile.user_type == 'lessor':
                        try:
                            lessor = Lessor.objects.get(email=user.email)
                            request.session['lessor_id'] = lessor.lessor_id
                            request.session.save()
                            return redirect('lessor_index')
                        except Lessor.DoesNotExist:
                            return redirect('lessor_details')
                except Profile.DoesNotExist:
                    messages.error(request, 'User profile not found. Please contact support.')
                    return render(request, 'users/login.html', {'form': form, 'title': 'log in'})
            else:
                messages.error(request, 'Invalid email or password.')
        
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form, 'title': 'log in'})



def Logout(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout



class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

################ index pages ##########################
@login_required(login_url='login')
def lessor_index(request):
    locations = Location.objects.all()
    lessor_id = request.session.get('lessor_id')
    lessor = Lessor.objects.get(lessor_id=lessor_id)
    warehouses = Warehouse.objects.filter(owner=lessor_id).order_by(F('warehouse_id').desc())
     # Fetch leases for the warehouses
    
   

   
    
    return render(request, 'users/lessor_index.html', {
        'locations': locations,
        'lessor_id': lessor_id,
        'lessor': lessor,
        'warehouses': warehouses,
       
    })




################ admin pages ##########################

def view_warehouse(request, warehouse_id):
    warehouse = Warehouse.objects.get(warehouse_id=warehouse_id)
    warehouse_facilities = warehouse.facilities.split(',')
    return render(request, 'users/view_warehouse.html', {'warehouse': warehouse, 'warehouse_facilities': warehouse_facilities})


@login_required(login_url='login')
def warehouse_list(request):
    warehouses = Warehouse.objects.prefetch_related('photos').all()
    
    sort = request.GET.get('sort', 'default')
    current_sort = 'Default Order'

    # Use the sorting function from sorting.py
    warehouses = sort_warehouses(warehouses, sort)

    # Set current_sort based on the selected option
    if sort == 'price_asc':
        current_sort = 'Price (Low to High)'
    elif sort == 'price_desc':
        current_sort = 'Price (High to Low)'
    elif sort == 'date_desc':
        current_sort = 'Date (Newest First)'
    elif sort == 'date_asc':
        current_sort = 'Date (Oldest First)'
    elif sort == 'available_places':
        current_sort = 'Available Places'
    elif sort == 'area':
        current_sort = 'area'

    return render(request, 'users/warehouse_list.html', {'warehouses': warehouses, 'current_sort': current_sort})

def warehouse_detail(request, warehouse_id):
    warehouse = Warehouse.objects.select_related('owner', 'location').get(warehouse_id=warehouse_id)
    warehouse_facilities = warehouse.facilities.split(',')
    reviews = WarehouseReview.objects.filter(warehouse=warehouse).select_related('tenant')  # Fetch reviews for the warehouse

    return render(request, 'users/warehouse_detail.html', {
        'warehouse': warehouse,
        'warehouse_facilities': warehouse_facilities,
        'reviews': reviews,
    })




    ############################## messages ##############################
def lessor_messages(request):
    # Get the lessor object for the logged-in user
    try:
        lessor = Lessor.objects.get(email=request.user.email)
    except Lessor.DoesNotExist:
        # Handle the case where the logged-in user is not a lessor
        return render(request, 'users/login.html', {'message': 'You are not registered as a lessor.'})

    # Get all tenants who have exchanged messages with the lessor
    tenants_with_messages = Tenant.objects.filter(
        Q(email__in=Message.objects.filter(receiver=request.user).values('sender__email')) |
        Q(email__in=Message.objects.filter(sender=request.user).values('receiver__email'))
    ).distinct()

    # Get the latest message and unread count for each tenant
    tenant_messages = []
    for tenant in tenants_with_messages:
        latest_message = Message.objects.filter(
            Q(sender=request.user, receiver__email=tenant.email) | 
            Q(sender__email=tenant.email, receiver=request.user)
        ).order_by('-timestamp').first()

        unread_count = Message.objects.filter(
            sender__email=tenant.email, 
            receiver=request.user, 
            is_read=False
        ).count()

        tenant_messages.append({
            'tenant': tenant,
            'latest_message': latest_message,
            'unread_count': unread_count
        })

    # Sort tenant_messages by the timestamp of the latest message
    tenant_messages.sort(key=lambda x: x['latest_message'].timestamp if x['latest_message'] else timezone.now(), reverse=True)

    return render(request, 'users/lessor_messages.html', {'tenant_messages': tenant_messages, 'lessor': lessor})



@login_required
def tenant_messages(request):
    # Get the tenant object for the logged-in user
    try:
        tenant = Tenant.objects.get(email=request.user.email)
    except Tenant.DoesNotExist:
        # Handle the case where the logged-in user is not a tenant
        return render(request, 'users/login.html', {'message': 'You are not registered as a tenant.'})

    # Get all lessors who have exchanged messages with the tenant
    lessors_with_messages = Lessor.objects.filter(
        Q(email__in=Message.objects.filter(receiver=request.user).values('sender__email')) |
        Q(email__in=Message.objects.filter(sender=request.user).values('receiver__email'))
    ).distinct()

    # Get the latest message and unread count for each lessor
    lessor_messages = []
    for lessor in lessors_with_messages:
        latest_message = Message.objects.filter(
            Q(sender=request.user, receiver__email=lessor.email) | 
            Q(sender__email=lessor.email, receiver=request.user)
        ).order_by('-timestamp').first()

        unread_count = Message.objects.filter(
            sender__email=lessor.email, 
            receiver=request.user, 
            is_read=False
        ).count()

        lessor_messages.append({
            'lessor': lessor,
            'latest_message': latest_message,
            'unread_count': unread_count
        })

    # Sort lessor_messages by the timestamp of the latest message
    lessor_messages.sort(key=lambda x: x['latest_message'].timestamp if x['latest_message'] else timezone.now(), reverse=True)

    return render(request, 'users/tenant_messages.html', {'lessor_messages': lessor_messages, 'tenant': tenant})



@login_required
def tenant_chat_view(request, lessor_id):
    lessor = get_object_or_404(Lessor,lessor_id=lessor_id)
    context = {
        'receiver': lessor,  # Lessor is the receiver in this context
    }
    return render(request, 'users/tenant_chat.html', context)      


@login_required
def lessor_chat_view(request, tenant_id):
    tenant = get_object_or_404(User, id=tenant_id)
    context = {
        'receiver': tenant,  # Tenant is the receiver in this context
    }
    return render(request, 'users/lessor_chat.html', context)      


@login_required
def message_detail(request, recipient_email):
    recipient = get_object_or_404(User, email=recipient_email)
    
    if request.method == 'POST':
        message_content = request.POST.get('message')
        if message_content:
            Message.objects.create(sender=request.user, receiver=recipient, message=message_content)
            return JsonResponse({"status": "success"})
        return JsonResponse({"status": "error", "message": "Empty message"})
    
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=recipient)) |
        (Q(sender=recipient) & Q(receiver=request.user))
    ).order_by('timestamp')
    
    return render(request, 'users/message_detail.html', {'recipient': recipient, 'messages': messages})

@login_required
def get_messages(request, recipient_email):
    recipient = get_object_or_404(User, email=recipient_email)
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=recipient)) |
        (Q(sender=recipient) & Q(receiver=request.user))
    ).order_by('timestamp')
    messages.filter(receiver=request.user).update(is_read=True)
    
    html = render_to_string('users/messages_list.html', {'messages': messages, 'request': request})
    return JsonResponse({"html": html})



################################ leases & Rented ############################################################

@login_required
def lease_offers(request):
    try:
        tenant = Tenant.objects.get(email=request.user.email)
        leases = Lease.objects.filter(tenant=tenant).order_by('-lease_start_date')
        print("the leases",leases)
    except Tenant.DoesNotExist:
        tenant = None
        leases = []

    context = {
        'tenant': tenant,
        'leases': leases,
    }
    return render(request, 'users/lease_offers.html', context)

@login_required
def reject_lease(request, lease_id):
    if request.method == 'POST':
        lease = get_object_or_404(Lease, lease_id=lease_id)
        lease.payment_status = 'Rejected'  # Update lease status to 'Rejected'
        lease.save()
        messages.success(request, 'Lease offer rejected successfully.')
    return redirect('lease_offers')


# @login_required
# def rented_warehouses(request):
#     try:
#         # Get the tenant based on the logged-in user's email
#         tenant = Tenant.objects.get(email=request.user.email)
#         # Fetch leases associated with the tenant
#         leases = Lease.objects.filter(tenant=tenant, payment_status='Paid').order_by('-lease_start_date')
#         print("The leases:", leases)
#     except Tenant.DoesNotExist:
#         tenant = None
#         leases = []

#     context = {
#         'tenant': tenant,
#         'leases': leases,
#     }
#     return render(request, 'warehouse/rented_warehouses.html', context)




@login_required
def rented_warehouses(request):
    user = request.user
    try:
        tenant = Tenant.objects.get(email=user.email)
        # Fetch leases associated with the tenant that are paid
        leases = Lease.objects.filter(tenant=tenant, payment_status='Paid').order_by('-lease_start_date')
        lease_expired = Lease.objects.filter(tenant=tenant, payment_status='Expired').order_by('-lease_start_date')
        # Fetch payments related to the leases
        payments = Payment.objects.filter(lease__in=leases)
        expired_payments = Payment.objects.filter(lease__in=lease_expired)

        # Create a dictionary to map lease IDs to payment details
        payment_dict = {payment.lease.lease_id: payment.amount for payment in payments}  # Ensure lease_id is accessed correctly
        expired_payment_dict = {payment.lease.lease_id: payment.amount for payment in expired_payments}
        
        print(tenant)

        if request.method == 'POST':
            form = WarehouseReviewForm(request.POST)
            if form.is_valid():
                warehouse_id = request.POST.get('warehouse_id')
                warehouse = get_object_or_404(Warehouse, warehouse_id=warehouse_id)

                # Check if a review already exists for this tenant and warehouse
                existing_review = WarehouseReview.objects.filter(tenant=tenant, warehouse=warehouse).first()
                if existing_review:
                    messages.error(request, 'You have already submitted a review for this warehouse.')
                else:
                    review = form.save(commit=False)  # Create a review instance but don't save it yet
                    review.tenant = tenant  # Set the tenant from the logged-in user
                    review.warehouse = warehouse  # Set the warehouse
                    review.save() 
                    form.save() # Save the review to the database
                    messages.success(request, 'Your review has been submitted successfully.')
                    print("saved review")
                    return redirect('rented_warehouses')  # Redirect to the same page after saving
            else:
                # Debugging: Print form errors
                print(form.errors)  # Print errors to the console for debugging
                messages.error(request, 'There was an error submitting your review. Please check the form.')
        else:
            form = WarehouseReviewForm()
        
    except Tenant.DoesNotExist:
        tenant = None
        leases = []
        payment_dict = {}
        expired_payment_dict = {}
        form = WarehouseReviewForm()

    context = {
        'tenant': tenant,
        'leases': leases,
        'payment_dict': payment_dict,
        'lease_expired': lease_expired,
        'payment_dict2': expired_payment_dict,
        'form': form,
    }
    return render(request, 'users/rented_warehouse.html', context)




@login_required
def download_lease_report(request, lease_id):
    # Fetch the lease, tenant, and payment data
    lease = get_object_or_404(Lease, lease_id=lease_id)
    tenant = lease.tenant  # Access the tenant directly from the lease
    payment = Payment.objects.filter(lease=lease, status='Paid')  # Assuming you want only paid payments
    convenience_fee_percentage = Decimal('0.02')
    convenience_fee = lease.total_amount * convenience_fee_percentage
    total_amount = lease.total_amount + convenience_fee  # Total amount including convenience fee
    payment = payment.first()
    # Prepare context for the PDF
    context = {
        'tenant': tenant,
        'lease': lease,
        'payment': payment,
        'convenience_fee': convenience_fee,
        'total_amount': total_amount,
        'current_date': timezone.now().date(),
    }
    print("The paynemtne:",payment)
    # Render the HTML template to a string
    html_string = render_to_string('users/download_lease_report.html', context)

    # Generate PDF using pdfkit
    cmd_options = {'quiet': None, 'enable-local-file-access': None}
    try:
        pdf = pdfkit.from_string(html_string, False, options=cmd_options)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="lease_report.pdf"'
        return response
    except Exception as e:
        # logger.error("pdfkit error: %s", str(e))  # Log the error output
        print("pdfkit error:", str(e))  # Print the error output to the console
        return HttpResponse("An error occurred while generating the PDF.", status=500)

###############################payments #################################################
from decimal import Decimal 
# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def payment(request, lease_id):
   
    if request.method == 'POST':
        # Fetch lease details
        lease = get_object_or_404(Lease, lease_id=lease_id)

        # Define convenience fee (e.g., 2% of the total amount)
        convenience_fee_percentage = Decimal('0.02')
        convenience_fee = lease.total_amount * convenience_fee_percentage
        total_amount = lease.total_amount + convenience_fee  # Total amount including convenience fee

        # Create a Razorpay order
        order_amount = float(total_amount * 100)  # Convert to float for JSON serialization
        order_currency = 'INR'
        order_receipt = str(lease.lease_id)
        
        # Create order
        order = razorpay_client.order.create(dict(amount=order_amount, currency=order_currency, receipt=order_receipt))
        order_id = order['id']

        # Render payment page with order details
        context = {
            'order_id': order_id,
            'lease': lease,
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'convenience_fee': convenience_fee,
            'total_amount': total_amount,
        }
        return render(request, 'users/payment.html', context)
    return redirect('lease_offers')


def payment_result(request, lease_id):
        if request.method == 'POST':
            order_id = request.POST.get('order_id')
            print(f"Received order_id: {order_id}") 
            payment_id = request.POST.get('payment_id') 
            lease = get_object_or_404(Lease, lease_id=lease_id)
            signature = request.FILES.get('signature')
            lease.tenant_signature =signature
            lease.save()
            # Verify payment
            try:
                payment = razorpay_client.payment.fetch(payment_id)
                if payment['status'] == 'captured':
                    # Save payment details
                    Payment.objects.create(
                        user=lease.tenant,
                        lease=lease,
                        order_id=order_id,
                        payment_id=payment['id'],
                        amount=lease.total_amount,  # Assuming this is the amount paid
                        status='Paid'
                    )
                    lease.payment_status = 'Paid'  # Update lease status
                    lease.save()

                     # Update the warehouse status to 2
                    warehouse = lease.warehouse
                    warehouse.status = 2  # Set status to 2
                    warehouse.save()
                    messages.success(request, 'Payment processed successfully.')
                    
                else:
                    messages.error(request, 'Payment failed. Please try again.')
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')

            return redirect('lease_offers')
        return redirect('lease_offers')


#############################extended technologies##########################################


def upload_image_share(request):
    download_link = None
    print("Upload image share function called.")
    email = None
    user= None  # Debugging: Function entry

    if request.method == 'POST':
        image_share = request.FILES.get('image_share')
        print(f"Received image share: {image_share}")  # Debugging: Print the uploaded image share

        if image_share:
            # Generate shares from the uploaded image
            server_share, user_share = generate_shares(image_share)
            print("Shares generated successfully.")  # Debugging

            session_email = request.session.get('email')
            if(session_email):
                user = get_object_or_404(User, email=session_email)
                email = user.email
                print(f"User email: {user}")  # Debugging: Print the user's email
            else:
                user = request.user
                email = user.email
                print(f"User email: {email}")  # Debugging: Print the user's email
            
            

            # Define the server share path
            server_path = os.path.join(settings.MEDIA_ROOT, 'auth', f'server_share_{email}.png')
            print(f"Server share path: {server_path}")  # Debugging: Print the server share path

            # Calculate the hash for the server share
            server_hash = calculate_hash(server_share)
            print(f"Server hash calculated: {server_hash}")  # Debugging: Print the server hash

            # Save the server share to the filesystem with the hash
            save_image_with_hash(server_share, server_path, server_hash)
            print("Server share saved to filesystem.")  # Debugging

            # Save the server share to the database
            server_share_instance = ServerShare(user=user)
            with open(server_path, 'rb') as image_file:
                server_share_instance.image.save(f'server_share_{email}.png', ContentFile(image_file.read()))
            server_share_instance.save()
            print("Server share instance saved to database.")  # Debugging

            # Use the server share as the user share
            unique_filename = f'user_share_{user.id}_{uuid.uuid4()}.png'
            user_share_path = os.path.join(settings.MEDIA_ROOT, f'auth/{unique_filename}')
            print(f"User share path: {user_share_path}")  # Debugging: Print the user share path
            
            # Save the user share (which is the same as the server share)
            save_image_with_hash(server_share, user_share_path, server_hash)
            print("User share saved to filesystem.")  # Debugging

            # Calculate and print the hash of the saved user share from the saved file
            saved_user_share_hash = get_hash_from_image(user_share_path)
            print(f"Hash of the saved user share: {saved_user_share_hash}")  # Debugging: Print the hash of the saved user share

            # Provide the download link for the user share
            download_link = f'/media/auth/{unique_filename}'
            messages.success(request, 'Image share uploaded and processed successfully!')
            print("Download link provided to user.")  # Debugging

    return render(request, 'users/upload_image_share.html', {'download_link': download_link})

def login_using_image(request):
    if request.method == 'POST':
        image_share = request.FILES.get('image_share')
        email = request.POST.get('email')
        print(f"Received email: {email}")  # Debugging: Print the received email
        print(f"Received image share: {image_share}")  # Debugging: Print the uploaded image share

        if image_share:
            user = get_object_or_404(User, email=email)
            print(f"User found: {user}")  # Debugging: Print the found user

            # Fetch the server share for the user
            server_share_instance = ServerShare.objects.filter(user=user).order_by('-created_at').first()
            if not server_share_instance:
                messages.error(request, "No server share found for this user.")
                print("No server share found for user.")  # Debugging
                return redirect('login_using_image')

            server_share_path = server_share_instance.image.path
            print(f"Server share path: {server_share_path}")  # Debugging: Print the server share path

            try:
                # Load and process the uploaded image
                uploaded_image = Image.open(image_share).convert('L')  # Convert to grayscale
                uploaded_image_array = np.array(uploaded_image)  # Convert to NumPy array
                print("Uploaded image processed successfully.")  # Debugging

                # Calculate the hash for the uploaded image share
                uploaded_hash = calculate_hash(uploaded_image_array)
                print(f"Uploaded hash calculated: {uploaded_hash}")  # Debugging: Print the uploaded hash

                # Retrieve the expected hash from the server share's metadata
                expected_server_hash = get_hash_from_image(server_share_path)
                print(f"Expected server hash: {expected_server_hash}")  # Debugging: Print the expected server hash

                # Compare the uploaded hash with the expected server hash
                if uploaded_hash != expected_server_hash:
                    messages.error(request, "Uploaded image share does not match the server share.")
                    print("Uploaded hash does not match the expected server hash.")  # Debugging
                    return redirect('login_using_image')

                # If hashes match, authenticate the user
                # Log in the user
                  # If hashes match, authenticate and login the user
                # user = authenticate(request, username=email, password=None)  # Password is None for image-based auth
                if user is not None:
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                
                    
                    if user.is_superuser:
                        return redirect('admin_dashboard')
                    
                    try:
                        profile = Profile.objects.get(user=user)
                        if profile.user_type == 'tenant':
                            try:
                                tenant = Tenant.objects.get(email=user.email)
                                request.session['tenant_id'] = tenant.tenant_id
                                request.session.save()
                                return redirect('index')
                            except Tenant.DoesNotExist:
                                return redirect('tenant_details')
                        elif profile.user_type == 'lessor':
                            try:
                                lessor = Lessor.objects.get(email=user.email)
                                request.session['lessor_id'] = lessor.lessor_id
                                request.session.save()
                                return redirect('lessor_index')
                            except Lessor.DoesNotExist:
                                return redirect('lessor_details')
                    except Profile.DoesNotExist:
                        messages.error(request, 'User profile not found. Please contact support.')
                        return render(request, 'users/login_using_image.html', {'title': 'log in'})
                else:
                    messages.error(request, 'Authentication failed. Please try again.')
            except Exception as e:
                messages.error(request, f"Authentication failed: {str(e)}")
        else:
            messages.error(request, 'Please upload an image share.')
    
    return render(request, 'users/login_using_image.html', {'title': 'log in'})
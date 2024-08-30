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
from .forms import LessorForm,TenantForm

from .models import Profile,Lessor,User,UnverifiedUser,Tenant,Message,Payment
from warehouse.models import Location,Warehouse,WarehousePhoto,Lease

from django.db.models import Q, Max


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

from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy

import razorpay

#################### index####################################### 
@login_required(login_url='login')
def index(request):
  
    if request.session.get('tenant_id') == None:
        redirect('tenant_details')
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
            return redirect('login')
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
    
   
    
    return render(request, 'users/lessor_index.html', {
        'locations': locations,
        'lessor_id': lessor_id,
        'lessor': lessor,
        'warehouses': warehouses
    })




################ admin pages ##########################

def view_warehouse(request, warehouse_id):
    warehouse = Warehouse.objects.get(warehouse_id=warehouse_id)
    warehouse_facilities = warehouse.facilities.split(',')
    return render(request, 'users/view_warehouse.html', {'warehouse': warehouse, 'warehouse_facilities': warehouse_facilities})


def warehouse_list(request):
    warehouses = Warehouse.objects.prefetch_related('photos').all()
    
    sort = request.GET.get('sort', 'default')
    current_sort = 'Default Order'

    if sort == 'price_asc':
        warehouses = warehouses.order_by('rental_price')
        current_sort = 'Price (Low to High)'
    elif sort == 'price_desc':
        warehouses = warehouses.order_by('-rental_price')
        current_sort = 'Price (High to Low)'
    elif sort == 'date_desc':
        warehouses = warehouses.order_by('-year_built')
        current_sort = 'Date (Newest First)'
    elif sort == 'date_asc':
        warehouses = warehouses.order_by('year_built')
        current_sort = 'Date (Oldest First)'
    else:
        # Default sorting
        warehouses = warehouses.order_by('-warehouse_id')
    return render(request, 'users/warehouse_list.html', {'warehouses': warehouses})

def warehouse_detail(request, warehouse_id):
    warehouse = Warehouse.objects.select_related('owner', 'location').get(warehouse_id=warehouse_id)
    warehouse_facilities = warehouse.facilities.split(',')
    return render(request, 'users/warehouse_detail.html', {
        'warehouse': warehouse,
        'warehouse_facilities': warehouse_facilities,
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



################################ leases  ############################################################

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
def rented_warehouses(request):
    try:
        # Get the tenant based on the logged-in user's email
        tenant = Tenant.objects.get(email=request.user.email)
        # Fetch leases associated with the tenant
        leases = Lease.objects.filter(tenant=tenant, payment_status='Paid').order_by('-lease_start_date')
        print("The leases:", leases)
    except Tenant.DoesNotExist:
        tenant = None
        leases = []

    context = {
        'tenant': tenant,
        'leases': leases,
    }
    return render(request, 'warehouse/rented_warehouses.html', context)


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
                    messages.success(request, 'Payment processed successfully.')
                    
                else:
                    messages.error(request, 'Payment failed. Please try again.')
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')

            return redirect('lease_offers')
        return redirect('lease_offers')
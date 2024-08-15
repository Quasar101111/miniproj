#users/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout,get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError

from django.db.models import F
from .forms import LessorRegisterForm,TenantRegisterForm,CustomAuthenticationForm
from .forms import LessorForm,TenantForm
from .models import Profile,Lessor,User,UnverifiedUser,Tenant
from warehouse.models import Location,Warehouse,WarehousePhoto
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import Paginator
from django.utils import timezone
from django.shortcuts import redirect
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives

from django.contrib.auth.decorators import user_passes_test
import random
import string

from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy

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
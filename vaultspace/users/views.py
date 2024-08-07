#users/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout,get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError


from .forms import LessorRegisterForm,TenantRegisterForm,CustomAuthenticationForm
from .forms import LessorForm,TenantForm
from .models import Profile,Lessor,User,UnverifiedUser,Tenant
from warehouse.models import Location,Warehouse,WarehousePhoto
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives

from django.utils import timezone
from django.shortcuts import redirect
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives


#################### index####################################### 
# @login_required(login_url='login')
def index(request):
  
    if request.session.get('tenant_id') == None:
        redirect('tenant_details')
    warehouses = Warehouse.objects.all().prefetch_related('photos').select_related('owner', 'location')
    return render(request, 'users/index.html', {'title':'index', 'warehouses': warehouses})

########### register here ##################################### 
def temp(request):
   
    
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
            messages.success(request, 'Lessor details have been saved successfully!')
            return redirect('index')
    else:
        if lessor:
            form = LessorForm(instance=lessor)
        else:
             form = LessorForm(initial={'email': request.user.email})
            
    context = {
        'title': 'temp',
        'lessor': lessor,
        'form': form
    }        
    return render(request, 'users/temp.html', context)

def register_tenant(request):
    if request.method == 'POST':
        form = TenantRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data.get('email')
            email=user.username
            try:
                existing_user = User.objects.get(email=user.username)
                messages.error(request, 'A user with this email already exists.')
                return render(request, 'users/register_tenant.html', {'form': form})
            except User.DoesNotExist:
                user = form.save(commit=False)
                user.username = email # Assign email as username
                user.set_password(form.cleaned_data['password1'])
              
                user.save()
                
                # Optionally create a profile if needed
                profile = Profile.objects.create(user=user, user_type='tenant')

                messages.success(request, 'Registration successful!')  # Optionally add success message
                return redirect('login')  # Redirect to a success page or login page
            except Exception as e:
                messages.error(request, '') 
                # messages.error(request, f'Error: {e}')
                # Handle exception, perhaps log it
        else:
            messages.error(request, 'Form is not valid.')
    else:
        form = TenantRegisterForm()
    
    return render(request, 'users/register_tenant.html', {'form': form})
          

def register_lessor(request):
    if request.method == 'POST':
        form = LessorRegisterForm(request.POST)
        if form.is_valid():
            
            user = form.save(commit=False)
            user.username = form.cleaned_data.get('email')
            email=user.username   
            try:
                existing_user = User.objects.get(email=user.username)
                messages.error(request, 'A user with this email already exists.')
                return render(request, 'users/register_tenant.html', {'form': form})
            except User.DoesNotExist:
                user = form.save(commit=False)
                user.username = email # Assign email as username
                user.set_password(form.cleaned_data['password1'])
              
                user.save()
                
                # Optionally create a profile if needed
                profile = Profile.objects.create(user=user, user_type='lessor')

                messages.success(request, 'Registration successful!')  # Optionally add success message
                return redirect('login')  # Redirect to a success page or login page
            except Exception as e:
                messages.error(request, '') 
                # messages.error(request, f'Error: {e}')
                # Handle exception, perhaps log it
        else:
            messages.error(request, 'Form is not valid.')
    else:
        form = LessorRegisterForm()
    
    return render(request, 'users/register_lessor.html', {'form': form})
   


################ user details################################################### 

@login_required
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
            messages.success(request, 'Lessor details have been saved successfully!')
            return redirect('lessor_index')
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
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                
                if user.is_superuser:
                    return redirect('admin_dashboard')  # Change 'admin_dashboard' to your admin's URL name
                else:
                    profile = Profile.objects.get(user=user)
                if profile.user_type == 'tenant':
                    try:
                        tenant = Tenant.objects.get(email=user.email)
                    except Tenant.DoesNotExist:
                    # Redirect to the lessor_details page if the Lessor does not exist
                        return redirect('tenant_details')  # Use the name of the URL pattern for lessor_details
                    tenant=Tenant.objects.get(email=user.email)
                    # Store lessor ID in session
                    request.session['tenant_id'] = tenant.tenant_id
                    request.session.save()
                   
                    return redirect('index')  # Change 'tenant_dashboard' to your tenant's URL name
                elif profile.user_type == 'lessor':
                    try:
                        lessor = Lessor.objects.get(email=user.email)
                    except Lessor.DoesNotExist:
                    # Redirect to the lessor_details page if the Lessor does not exist
                        return redirect('lessor_details')  # Use the name of the URL pattern for lessor_details
                    lessor=Lessor.objects.get(email=user.email)
                    # Store lessor ID in session
                    request.session['lessor_id'] = lessor.lessor_id
                    request.session.save()
                   
                    return redirect('lessor_index') 
    else:
        form = CustomAuthenticationForm()
        
    return render(request, 'users/login.html', {'form': form, 'title': 'log in'})



def Logout(request):
    logout(request)
    return redirect('index')  # Redirect to login page after logout

################ index pages ##########################
def lessor_index(request):
    locations = Location.objects.all()
    lessor_id = request.session.get('lessor_id')
    lessor = Lessor.objects.get(lessor_id=lessor_id)
    warehouses = Warehouse.objects.filter(owner=lessor_id)
    
   
    
    return render(request, 'users/lessor_index.html', {
        'locations': locations,
        'lessor_id': lessor_id,
        'lessor': lessor,
        'warehouses': warehouses
    })






def view_warehouse(request, warehouse_id):
    warehouse = Warehouse.objects.get(warehouse_id=warehouse_id)
    warehouse_facilities = warehouse.facilities.split(',')
    return render(request, 'users/view_warehouse.html', {'warehouse': warehouse, 'warehouse_facilities': warehouse_facilities})
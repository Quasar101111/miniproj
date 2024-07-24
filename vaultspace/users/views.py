#users/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm

from .forms import LessorRegisterForm,TenantRegisterForm,CustomAuthenticationForm
from .forms import LessorForm
from .models import Profile,Lessor,User
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

from django.conf import settings
# views.py

from django.shortcuts import redirect
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives


#################### index####################################### 
def index(request):
	return render(request, 'users/index.html', {'title':'index'})

########### register here ##################################### 


def register_tenant(request):
    if request.method == 'POST':
        form = TenantRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data.get('email') 
            user.save()
            profile = Profile(user=user, user_type='tenant')
            profile.save()
            # Email sending logic
            username = user.email
            htmly = get_template('users/Email.html')
            d = {'username': username}
            subject, from_email, to = 'Welcome', 'your_email@gmail.com', user.email
            html_content = htmly.render(d)
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('login')  # Redirect to a success page
    else:
        form = TenantRegisterForm()
    return render(request, 'users/register_tenant.html', {'form': form})

def register_lessor(request):
    if request.method == 'POST':
        form = LessorRegisterForm(request.POST)
        if form.is_valid():
            
            user = form.save(commit=False)
            user.username = form.cleaned_data.get('email') 
            try:
                existing_user = User.objects.get(email=user)
                messages.error(request, 'A user with this email already exists.')
                return render(request, 'users/register_lessor.html', {'form': form})
            except:

           
                user.save()
            
                profile = Profile(user=user, user_type='lessor')
                profile.save()
                # Email sending logic
                username = user.email
                htmly = get_template('users/Email.html')
                d = {'username': username}
                subject, from_email, to = 'Welcome', 'your_email@gmail.com', user.email
                html_content = htmly.render(d)
                msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
                msg.attach_alternative(html_content, "text/html")
                msg.send()

                messages.success(request, f'Your account has been created! You are now able to log in')
                return redirect('login')  # Redirect to a success page
    else:
        form = LessorRegisterForm()
    return render(request, 'users/register_lessor.html', {'form': form})






@login_required
def lessor_details(request):
    try:
        # Get the Lessor instance for the logged-in user
        lessor = Lessor.objects.get(email=request.user.email)
    except Lessor.DoesNotExist:
        # If Lessor instance does not exist, set to None
        lessor = None
    if request.method == 'POST':
        form = LessorForm(request.POST, request.FILES)
        if form.is_valid():
            lessor = form.save(commit=False)
            lessor.email = request.user.email  # Set email to the logged-in user's email
            lessor.save()
            messages.success(request, 'Lessor details have been saved successfully!')
            return redirect('index')
    else:
        form = LessorForm(initial={'email': request.user.email})
    return render(request, 'users/lessor_details.html', {'form': form, 'title': 'Lessor Registration'})
################ login forms################################################### 
def Login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # here username=email from forms
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome {user.email}!')
                return redirect('index')
            else:
               for error in form.errors.values():
                messages.error(request, error)
                messages.error(request, 'Invalid email or password.')
    else:
        form = CustomAuthenticationForm()
        
    return render(request, 'users/login.html', {'form': form, 'title': 'log in'})



def Logout(request):
    return redirect('login')  # Redirect to login page after logout
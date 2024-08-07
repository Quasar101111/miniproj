# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile
from .models import Lessor,models,Tenant

from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def email_exist(value):
    if User.objects.filter(email=value).exists():
        return forms.ValidationError("Profile with this Email Address already exists")
    
class LessorRegisterForm(UserCreationForm):
    email = forms.EmailField()
    user_type = forms.CharField(widget=forms.HiddenInput(), initial='lessor')

    class Meta:
        model = User
        fields = ['email', 'password1','user_type']
class TenantRegisterForm(UserCreationForm):
    email = forms.EmailField()
   

    class Meta:
        model = User
        fields = ['email', 'password1']




class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email"
      
    )
    def clean_username(self):
        email = self.cleaned_data.get('username')
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError("Enter a valid email address.")
        return email 
    
class LessorForm(forms.ModelForm):
        class Meta:
            model = Lessor
            fields = ['lessor_name','email','identity_proof','contact_number', 'photo']
            widgets = {
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
            }


class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['tenant_name', 'email', 'identity_proof', 'contact_number', 'photo', 'state', 'city']
        widgets = {
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
        }

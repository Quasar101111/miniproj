# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile
from .models import Lessor, models, Tenant

from django.core.validators import validate_email
from django.core.exceptions import ValidationError

import re


def email_exist(value):
    if User.objects.filter(email=value).exists():
        return forms.ValidationError("Profile with this Email Address already exists")
    
class LessorRegisterForm(UserCreationForm):
    email = forms.CharField()
    user_type = forms.CharField(widget=forms.HiddenInput(), initial='lessor')

    class Meta:
        model = User
        fields = ['email', 'password1','user_type']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Enter a valid email address.")
        return email


class TenantRegisterForm(UserCreationForm):
    email = forms.CharField()
    user_type = forms.CharField(widget=forms.HiddenInput(), initial='tenant')

    class Meta:
        model = User
        fields = ['email', 'password1','user_type']
    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Enter a valid email address.")
        return email    





class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Email"
      
    )
    def clean_username(self):
        email = self.cleaned_data.get('username')
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError("Enter your registered  email address.")
        return email 
    

class LessorForm(forms.ModelForm):
        class Meta:
            model = Lessor
            fields = ['lessor_name','email','identity_proof','contact_number', 'photo']
            widgets = {
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
            }
        def clean_lessor_name(self):
            lessor_name = self.cleaned_data.get('lessor_name')
            if not lessor_name:
                raise forms.ValidationError("Lessor name is required.")
            if len(lessor_name) < 3:
                raise forms.ValidationError("Lessor name must be at least 3 characters long.")
            if len(lessor_name) > 100:
                raise forms.ValidationError("Lessor name must not exceed 100 characters.")
            if re.search(r'\d', lessor_name):
                raise forms.ValidationError("Lessor name cannot contain numbers.")
            return lessor_name


        def clean_email(self):
            email = self.cleaned_data.get('email')
            try:
                validate_email(email)
            except ValidationError:
                raise forms.ValidationError("Enter a valid email address.")
            return email

        def clean_identity_proof(self):
            identity_proof = self.cleaned_data.get('identity_proof')
            if identity_proof:
                if identity_proof.size > 5 * 1024 * 1024:  # 5 MB limit
                    raise forms.ValidationError("Identity proof file size should not exceed 5 MB.")
                ext = identity_proof.name.split('.')[-1].lower()
                if ext not in ['pdf', 'jpg', 'jpeg', 'png']:
                    raise forms.ValidationError("Only PDF, JPG, JPEG, and PNG files are allowed for identity proof.")
            else:
                raise forms.ValidationError("Identity proof is required.")
            return identity_proof

        def clean_contact_number(self):
            contact_number = self.cleaned_data.get('contact_number')
            if not contact_number:
                raise forms.ValidationError("Contact number is required.")
            if not contact_number.isdigit() or len(contact_number) != 10:
                raise forms.ValidationError("Contact number must be a 10-digit number.")
            return contact_number

        def clean_photo(self):
            photo = self.cleaned_data.get('photo')
            if photo:
                if photo.size > 5 * 1024 * 1024:  # 5 MB limit
                    raise forms.ValidationError("Photo size should not exceed 5 MB.")
                ext = photo.name.split('.')[-1].lower()
                if ext not in ['jpg', 'jpeg', 'png']:
                    raise forms.ValidationError("Only JPG, JPEG, and PNG files are allowed for photo.")
            else:
                raise forms.ValidationError("Photo is required.")
            return photo

class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['tenant_name', 'email', 'identity_proof', 'contact_number', 'photo', 'state', 'city']
        widgets = {
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
        }

    def clean_tenant_name(self):
        tenant_name = self.cleaned_data.get('tenant_name')
        if not tenant_name:
            raise forms.ValidationError("Tenant name is required.")
        if len(tenant_name) < 3:
            raise forms.ValidationError("Tenant name must be at least 3 characters long.")
        if len(tenant_name) > 100:
            raise forms.ValidationError("Tenant name must not exceed 100 characters.")
        if re.search(r'\d', tenant_name):
            raise forms.ValidationError("Tenant name cannot contain numbers.")
        return tenant_name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Enter a valid email address.")
        return email

    def clean_identity_proof(self):
        identity_proof = self.cleaned_data.get('identity_proof')
        if identity_proof:
            if identity_proof.size > 5 * 1024 * 1024:  # 5 MB limit
                raise forms.ValidationError("Identity proof file size should not exceed 5 MB.")
            ext = identity_proof.name.split('.')[-1].lower()
            if ext not in ['pdf', 'jpg', 'jpeg', 'png']:
                raise forms.ValidationError("Only PDF, JPG, JPEG, and PNG files are allowed for identity proof.")
        else:
            raise forms.ValidationError("Identity proof is required.")
        return identity_proof

    def clean_contact_number(self):
        contact_number = self.cleaned_data.get('contact_number')
        if not contact_number:
            raise forms.ValidationError("Contact number is required.")
        if not contact_number.isdigit() or len(contact_number) != 10:
            raise forms.ValidationError("Contact number must be a 10-digit number.")
        return contact_number

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            if photo.size > 5 * 1024 * 1024:  # 5 MB limit
                raise forms.ValidationError("Photo size should not exceed 5 MB.")
            ext = photo.name.split('.')[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png']:
                raise forms.ValidationError("Only JPG, JPEG, and PNG files are allowed for photo.")
        else:
            raise forms.ValidationError("Photo is required.")
        return photo

    def clean_state(self):
        state = self.cleaned_data.get('state')
        if not state:
            raise forms.ValidationError("State is required.")
        if len(state) > 100:
            raise forms.ValidationError("State name must not exceed 100 characters.")
        if re.search(r'\d', state):
            raise forms.ValidationError("State name cannot contain numbers.")
        return state

    def clean_city(self):
        city = self.cleaned_data.get('city')
        if not city:
            raise forms.ValidationError("City is required.")
        if len(city) > 100:
            raise forms.ValidationError("City name must not exceed 100 characters.")
        if re.search(r'\d', city):
            raise forms.ValidationError("City name cannot contain numbers.")
        return city    
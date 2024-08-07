# users/models.py

from django.db import models
from django.contrib.auth.models import User
import secrets
from django.utils import timezone
from django.core.mail import send_mail

class Profile(models.Model):
    USER_TYPES = (
        ('lessor', 'Lessor'),
        ('tenant', 'Tenant'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=6, choices=USER_TYPES)
    is_verified = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user.email} Profile'
    

    


class UnverifiedUser(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    otp = models.CharField(max_length=6, blank=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    resend_attempts = models.IntegerField(default=0)
    last_resend_time = models.DateTimeField(blank=True, null=True)
    user_type = models.CharField(max_length=10)  # Add user type field

    def generate_otp(self):
        self.otp = secrets.token_hex(3)  # Generate a 6-digit OTP
        self.otp_created_at = timezone.now()
        self.save()

    def send_otp_email(self):
        subject = 'Your OTP Verification Code'
        message = f'Your OTP verification code is {self.otp}. It is valid for 15 minutes.'
        email_from = 'vaultspace07@gmail.com'
        recipient_list = self.email
        send_mail(subject, message, email_from, recipient_list)

    def verify_otp(self, entered_otp):
        if self.otp == entered_otp and self.otp_created_at >= timezone.now() - timezone.timedelta(minutes=15):
            return True
        return False
    
    def can_resend_otp(self):
        if self.last_resend_time and self.last_resend_time >= timezone.now() - timezone.timedelta(minutes=1):
            return False
        return True
class Lessor(models.Model):
      
        lessor_id = models.AutoField(primary_key=True)
        lessor_name = models.CharField(max_length=50)
        email = models.EmailField(max_length=50)
        contact_number = models.CharField(max_length=50)
        photo = models.ImageField(upload_to='lessor_photos/')
        identity_proof = models.FileField(upload_to='lessor_id/', null=True, blank=True)
        def __str__(self):
            return f'Name: {self.lessor_name} '
        
class Tenant(models.Model):
      
    tenant_id = models.AutoField(primary_key=True)
    tenant_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    contact_number = models.CharField(max_length=50)
    photo = models.ImageField(upload_to='tenant_photos/')
    identity_proof = models.FileField(upload_to='tenant_id/', null=True, blank=True)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)    
                                        
    def __str__(self):
       return f'Tenant: {self.tenant_name} ({self.tenant_id})'        
        
        
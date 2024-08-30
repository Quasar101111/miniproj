# users/models.py

from django.db import models,connection
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

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"


def drop_message_table():
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS users_message CASCADE;")

# Call this function before running migrations           


class Payment(models.Model):
    user = models.ForeignKey('Tenant', on_delete=models.CASCADE)
    lease = models.ForeignKey('warehouse.Lease', on_delete=models.CASCADE)  # Changed to string reference
    order_id = models.CharField(max_length=255)
    payment_id = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    status = models.CharField(max_length=50)  # e.g., 'Paid', 'Failed'
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} for Lease {self.lease.lease_id}"
    
  
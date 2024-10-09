# warehouse/models.py

from django.db import models
import secrets
from django.utils import timezone
from django.utils.timezone import now

from users.models import Lessor, Tenant
import os


class Location(models.Model):
    location_id = models.AutoField(primary_key=True)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)

    def __str__(self):
        return f"Location {self.location_id}: {self.city}, {self.state}"

class Warehouse(models.Model):
    warehouse_id = models.AutoField(primary_key=True)
    owner = models.ForeignKey('users.Lessor', on_delete=models.CASCADE)
    location = models.ForeignKey('Location', on_delete=models.CASCADE)
    area = models.DecimalField(max_digits=10,decimal_places=2)
    ownership_documents = models.FileField(upload_to='ownership_docs/', blank=True, null=True)
    facilities = models.CharField(max_length=255)
    year_built = models.DateField()
    landmarks = models.CharField(max_length=255, blank=True, null=True)
    rental_price = models.DecimalField(max_digits=10, decimal_places=2)
    terms_cond = models.TextField()
    status = models.IntegerField(default=1)  # Default status is set to 1
    length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Length in meters
    breadth = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Breadth in meters
    height = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Height in meters

    def __str__(self):
        return f"Warehouse {self.warehouse_id}"

class WarehousePhoto(models.Model):
    warehouse = models.ForeignKey(Warehouse, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='warehouse_photos/')
    
    def __str__(self):
         return f"Photo of Warehouse ID: {str(self.warehouse)}"




def upload_signature_path(instance, filename):
    # Get the file extension
    ext = filename.split('.')[-1]
    
    # Create a unique filename using the lease_id, role, and current timestamp
    new_filename = f"{instance.lease_id}_{instance.role}_{now().strftime('%Y%m%d%H%M%S')}.{ext}"
    
    # Return the path where the file will be saved
    return os.path.join('lease_signatures/', new_filename)


class Lease(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Rejected', 'Rejected'),
    ]

    lease_id = models.AutoField(primary_key=True)
    warehouse = models.ForeignKey('Warehouse', on_delete=models.CASCADE)
    tenant = models.ForeignKey('users.Tenant', on_delete=models.CASCADE)
    lease_start_date = models.DateField()
    lease_end_date = models.DateField()
    rental_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    
    last_updated = models.DateTimeField(auto_now=True)
    tenant_signature = models.ImageField(upload_to=upload_signature_path, null=True, blank=True)
    lessor_signature = models.ImageField(upload_to=upload_signature_path, null=True, blank=True)


    def __str__(self):
        return f"Lease {self.lease_id} - {self.warehouse} - {self.tenant}"

   
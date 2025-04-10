# warehouse/models.py

from django.db import models
import secrets
from django.utils import timezone
from django.utils.timezone import now

from users.models import Lessor, Tenant
import os
from blockchain.service import BlockchainService

# Remove Map import since we're using lazy loading

class Location(models.Model):
    location_id = models.AutoField(primary_key=True)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)

    def __str__(self):
        return f"Location {self.location_id}: {self.city}, {self.state}"

class Warehouse(models.Model):
    warehouse_id = models.AutoField(primary_key=True)
    name=models.CharField(max_length=255,blank=True)
    owner = models.ForeignKey('users.Lessor', on_delete=models.CASCADE)
    location = models.ForeignKey('Location', on_delete=models.CASCADE,blank=True,null=True)
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
    popularity_score = models.FloatField(default=0.0)
    last_activity = models.DateTimeField(auto_now=True)
    blockchain_tx = models.CharField(max_length=66, blank=True)

    def __str__(self):
        return f"Warehouse {self.warehouse_id}"

    def save(self, *args, **kwargs):
        if self.location:
            # Extract city and state from the location string
            location_parts = self.location.split(',')
            if len(location_parts) >= 2:
                city = location_parts[0].strip()
                state = location_parts[1].strip()
                
                # Create or get the Location object
                location_obj, created = Location.objects.get_or_create(
                    city=city,
                    state=state
                )
                
                # Set the location and name
                self.location = location_obj
                self.name = f"{city}, {state}"
            else:
                # If we can't parse the location, use the raw string
                self.name = self.location
        super().save(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     # First save to get the ID
    #     super().save(*args, **kwargs)

    #     if not self.blockchain_tx:  # Only if not already on blockchain
    #         service = BlockchainService()
            
    #         try:
    #             # Use the related name from Map model
    #             map_location = self.map_location
    #             location_string = f"{map_location.latitude},{map_location.longitude}"
    #         except:
    #             location_string = self.landmarks or "No location"
            
    #         tx = service.contract.functions.addWarehouse(
    #             self.name or f"Warehouse {self.warehouse_id}",
    #             location_string,
    #             int(float(self.area)),
    #             int(float(self.rental_price))
    #         ).build_transaction(service.get_tx_params())
            
    #         signed_tx = service.w3.eth.account.sign_transaction(
    #             tx, os.getenv('PRIVATE_KEY'))
    #         # Use raw_transaction instead of rawTransaction
    #         tx_hash = service.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    #         self.blockchain_tx = tx_hash.hex()
    #         super().save(update_fields=['blockchain_tx'])

class WarehousePhoto(models.Model):
    warehouse = models.ForeignKey(Warehouse, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='warehouse_photos/')
    
    def __str__(self):
         return f"Photo of Warehouse ID: {str(self.warehouse)}"




def upload_signature_path(instance, filename):
    # Get the file extension
    ext = filename.split('.')[-1]
    
    
    # Create a unique filename using the lease_id, role, and current timestamp
    random_string = secrets.token_hex(8)  # Generate a random string
    new_filename = f"{random_string}_{now().strftime('%Y%m%d%H%M%S')}.{ext}"
    
    # Return the path where the file will be saved
    return os.path.join('lease_signatures/', new_filename)


class Lease(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Rejected', 'Rejected'),
        ('Expired', 'Expired'),
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
    blockchain_tx = models.CharField(max_length=66, blank=True)

    def __str__(self):
        return f"Lease {self.lease_id} - {self.warehouse} - {self.tenant}"
    
    def save(self, *args, **kwargs):
        if not self.pk:
            service = BlockchainService()
            tx = service.contract.functions.createLease(
                self.warehouse.warehouse_id,
                self.tenant.wallet_address,
                int(float(self.rental_amount)),
                int(self.lease_start_date.timestamp()),
                int(self.lease_end_date.timestamp())
            ).build_transaction(service.get_tx_params())
            
            signed_tx = service.w3.eth.account.sign_transaction(
                tx, os.getenv('PRIVATE_KEY'))
            # Use raw_transaction instead of rawTransaction
            tx_hash = service.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            self.blockchain_tx = tx_hash.hex()
        
        super().save(*args, **kwargs)

class WarehouseReview(models.Model):
    
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='reviews')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(0, 6)])  # Rating from 1 to 5
    opinion = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.tenant} for {self.warehouse} - Rating: {self.rating}"


class WarehouseAvailability(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="availabilities")
    start_date = models.DateField()
    end_date = models.DateField()
    booked_by = models.ForeignKey(Lessor, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('available', 'Available'), ('booked', 'Booked')],
        default='available'
    )

    def __str__(self):
        return f"{self.warehouse.name} ({self.start_date} - {self.end_date})"
# warehouse/models.py

from django.db import models
import secrets
from django.utils import timezone

from users.models import Lessor


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
    area = models.CharField(max_length=50)
    ownership_documents = models.FileField(upload_to='ownership_docs/', blank=True, null=True)
    facilities = models.CharField(max_length=255)
    year_built = models.DateField()
    landmarks = models.CharField(max_length=255, blank=True, null=True)
    rental_price = models.DecimalField(max_digits=10, decimal_places=2)
    terms_cond = models.TextField()
    status = models.IntegerField(default=1)  # Default status is set to 1

    def __str__(self):
        return f"Warehouse {self.warehouse_id}"

class WarehousePhoto(models.Model):
    warehouse = models.ForeignKey(Warehouse, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='warehouse_photos/')
    
    def __str__(self):
         return f"Photo of Warehouse ID: {str(self.warehouse)}"
   
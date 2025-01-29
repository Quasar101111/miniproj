# inventory/models.py
from django.db import models
from django.core.exceptions import ValidationError
from warehouse.models import Warehouse




def calculate_available_dimensions(warehouse):
    """Calculate the available dimensions and area of the warehouse."""
    used_length = warehouse.usage.used_length
    used_breadth = warehouse.usage.used_breadth
    used_height = warehouse.usage.used_height

    available_length = warehouse.length - used_length
    available_breadth = warehouse.breadth - used_breadth
    available_height = warehouse.height - used_height

    available_area = available_length * available_breadth

    return available_length, available_breadth, available_height, available_area

class WarehouseUsage(models.Model):
    warehouse = models.OneToOneField(Warehouse, on_delete=models.CASCADE, related_name='usage')
    used_length = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    used_breadth = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    used_height = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Usage for Warehouse {self.warehouse.warehouse_id}"


class Zone(models.Model):
    """Represents a zone within the inventory system."""
    RECEIVING = 'RECEIVING'
    STORAGE = 'STORAGE'
    PICKING = 'PICKING'
    ZONE_TYPES = [
        (RECEIVING, 'Receiving Area'),
        (STORAGE, 'Storage Area'),
        (PICKING, 'Picking Area'),
    ]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    zone_type = models.CharField(max_length=20, choices=ZONE_TYPES)
    length = models.DecimalField(max_digits=10, decimal_places=2, help_text="Length of the zone in meters.")
    breadth = models.DecimalField(max_digits=10, decimal_places=2, help_text="Breadth of the zone in meters.")
    height = models.DecimalField(max_digits=10, decimal_places=2, help_text="Height of the zone in meters.")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def clean(self):
        """Custom validation logic to ensure the zone fits within the warehouse and updates warehouse used space."""
        warehouse = self.warehouse
        
        # Calculate available dimensions
        available_length, available_breadth, available_height, _ = calculate_available_dimensions(warehouse)

        # Check if new zone dimensions are within the warehouse's available dimensions
        if self.length > available_length or self.breadth > available_breadth or self.height > available_height:
            raise ValidationError("Zone dimensions exceed available warehouse dimensions.")

    def save(self, *args, **kwargs):
        self.clean()

        warehouse_usage = self.warehouse.usage
        
        warehouse_usage.used_length += self.length
        warehouse_usage.used_breadth += self.breadth
        warehouse_usage.used_height += self.height
        
        warehouse_usage.save()
        
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        warehouse_usage = self.warehouse.usage
        
        warehouse_usage.used_length -= self.length
        warehouse_usage.used_breadth -= self.breadth
        warehouse_usage.used_height -= self.height
        
        warehouse_usage.save()
        
        super().delete(*args, **kwargs)

class InventoryItem(models.Model):
    """Represents an item stored in the inventory."""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    item_length = models.FloatField(help_text="Length of the item in meters.")
    item_width = models.FloatField(help_text="Width of the item in meters.")
    item_height = models.FloatField(help_text="Height of the item in meters.")

    def __str__(self):
        return self.name

class InventoryLocation(models.Model):
    """Represents a storage location within a zone, with dimensions and item details."""
    id = models.AutoField(primary_key=True)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    item = models.ForeignKey(InventoryItem, on_delete=models.SET_NULL, null=True, blank=True)
    length = models.FloatField(help_text="Length of the storage space in meters.")
    width = models.FloatField(help_text="Width of the storage space in meters.")
    height = models.FloatField(help_text="Height of the storage space in meters.")
    stackable = models.BooleanField(default=False, help_text="Whether the item can be stacked.")
    max_stacking_height = models.FloatField(help_text="Maximum number of stacking layers allowed based on the item height.")
    aisle_width = models.FloatField(help_text="Width of the aisles between storage units.")
    item_count = models.PositiveIntegerField(default=0, help_text="Number of items in this location.")

    def __str__(self):
        return f"Location {self.id} in {self.zone.name}"

    def clean(self):
        """Custom validation logic to ensure the item fits within the location."""
        if self.item:
            total_item_volume = self.item.item_length * self.item.item_width * self.item.item_height * self.item_count
            location_volume = self.length * self.width * self.height

            # Check if item dimensions are within the storage location dimensions
            if (self.item.item_length > self.length or
                self.item.item_width > self.width or
                self.item.item_height > self.height):
                raise ValidationError("Item dimensions exceed storage location dimensions.")
            
            # Check if the item can be stacked
            if self.stackable:
                max_item_height = self.item.item_height * self.max_stacking_height
                if max_item_height > self.height:
                    raise ValidationError("Stacking height exceeds storage location height.")
                
                stackable_volume = self.length * self.width * max_item_height
                if total_item_volume > stackable_volume:
                    raise ValidationError("Total volume of stacked items exceeds storage location capacity.")
            else:
                if total_item_volume > location_volume:
                    raise ValidationError("Total volume of items exceeds storage location capacity.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
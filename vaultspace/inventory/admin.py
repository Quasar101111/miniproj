from django.contrib import admin
from .models import Zone, InventoryItem, InventoryLocation,WarehouseUsage


admin.site.register(Zone)
admin.site.register(InventoryItem)
admin.site.register(InventoryLocation)
admin.site.register(WarehouseUsage)
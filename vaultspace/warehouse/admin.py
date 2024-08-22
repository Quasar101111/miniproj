# warehouse/admin.py 
from django.contrib import admin
from .models import Location, Warehouse, WarehousePhoto, Lease
from django.db import models
from django.forms import Textarea

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('location_id', 'state', 'city')
    search_fields = ('state', 'city')
    list_filter = ('state',)

class WarehousePhotoInline(admin.TabularInline):
    model = WarehousePhoto
    extra = 1  # Number of extra forms to display

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('warehouse_id', 'owner', 'location', 'area', 'rental_price', 'status')
    search_fields = ('owner__name', 'location__city', 'area')
    list_filter = ('status', 'location__state')
    inlines = [WarehousePhotoInline]
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 40})},
    }

@admin.register(WarehousePhoto)
class WarehousePhotoAdmin(admin.ModelAdmin):
    list_display = ('warehouse', 'image')
    search_fields = ('warehouse__owner__name',)

admin.site.register(Lease)
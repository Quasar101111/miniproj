import os
import csv
from django.core.management.base import BaseCommand
from django.conf import settings  # Import Django settings
from warehouse.models import WarehouseReview, Lease, Warehouse
from users.models import Tenant
from map.models import Map
from django.utils import timezone

class Command(BaseCommand):
    help = 'Export tenant interactions with enhanced features for ML training'

    def handle(self, *args, **kwargs):
        # Save in Django's `media/exports/` directory
        export_dir = os.path.join(settings.MEDIA_ROOT, 'exports')
        os.makedirs(export_dir, exist_ok=True)  # Ensure the directory exists

        # Add timestamp to filename
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        file_path = os.path.join(export_dir, f'warehouse_data_{timestamp}.csv')

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)

                # Header row
                writer.writerow([
                    'tenant_id', 'warehouse_id', 'rating', 'leased',
                    'area', 'length', 'breadth', 'height', 'rental_price',
                    'facilities',
                    'tenant_lat', 'tenant_long', 'warehouse_lat', 'warehouse_long'
                ])

                # Export data
                for review in WarehouseReview.objects.select_related('warehouse', 'tenant').all():
                    self.write_row(writer, review.tenant, review.warehouse, review.rating)

                for lease in Lease.objects.select_related('warehouse', 'tenant').all():
                    self.write_row(writer, lease.tenant, lease.warehouse, 5)  # Assume leases get max rating

            self.stdout.write(self.style.SUCCESS(f'Data export completed! File saved at {file_path}'))

        except PermissionError:
            self.stdout.write(self.style.ERROR(
                f"Permission denied. Make sure:\n"
                f"1. The file isn't open in another program (like Excel)\n"
                f"2. You have write permissions to: {export_dir}\n"
                f"3. Try running as administrator if needed"
            ))

    def write_row(self, writer, tenant, warehouse, rating):
        """Helper function to extract features and write a row to the CSV file."""
        try:
            map_entry = Map.objects.filter(warehouse=warehouse).latest('last_updated')
            warehouse_lat, warehouse_long = map_entry.latitude, map_entry.longitude
        except Map.DoesNotExist:
            warehouse_lat, warehouse_long = 0.0, 0.0

        facilities = ','.join(warehouse.facilities.split(',')) if warehouse.facilities else 'None'

        writer.writerow([
            tenant.tenant_id,
            warehouse.warehouse_id,
            rating,
            1,  # Indicate that the warehouse was leased/viewed
            warehouse.area or 0.0,
            warehouse.length or 0.0,
            warehouse.breadth or 0.0,
            warehouse.height or 0.0,
            warehouse.rental_price or 0.0,
            facilities,
            tenant.latitude or 0.0,
            tenant.longitude or 0.0,
            warehouse_lat,
            warehouse_long
        ])

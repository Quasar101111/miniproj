from django.core.management.base import BaseCommand
from warehouse.models import Lease
from users.models import Tenant
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'Send email notifications for leases ending in 5 days'

    def handle(self, *args, **kwargs):
        # Calculate the date 5 days from now
        five_days_from_now = timezone.now().date() + timedelta(days=5)

        # Filter leases ending in 5 days
        leases_ending_soon = Lease.objects.filter(lease_end_date=five_days_from_now)

        # Send email to each tenant
        for lease in leases_ending_soon:
            tenant = lease.tenant
            
            send_mail(
                'Lease Expiry Notification',
                f'Dear {tenant.name}, your lease for {lease.warehouse} is ending on {lease.lease_end_date}.',
                'from@example.com',  # Replace with your sender email
                [tenant.email],  # Tenant's email
                fail_silently=False,
            )

        self.stdout.write(self.style.SUCCESS(f'Emails sent for leases ending on {five_days_from_now}'))

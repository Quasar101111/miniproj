from django.utils import timezone
from django.core.mail import send_mail
from .models import Lease,Warehouse
from users.models import Tenant
import logging

logger = logging.getLogger(__name__)

def send_lease_expiry_notifications_and_cleanup():
    today = timezone.now().date()
    
    # Expired leases: All leases that ended before today and still not marked expired
    expired_leases = Lease.objects.filter(
        lease_end_date__lt=today,  # All dates before today
        payment_status__in=['Paid', 'Pending']  # Include both statuses
    )
    
    # Update payment status and warehouse availability
    for lease in expired_leases:
        lease.payment_status = 'Expired'
        lease.save()
        
        # Only update warehouse if it's still marked as occupied
        if lease.warehouse.status != 1:
            lease.warehouse.status = 1  # Available
            lease.warehouse.save()
            
        logger.info(f"Updated lease {lease.lease_id} (ended {lease.lease_end_date}) to Expired")

    # Notifications for upcoming expiries (next 5 days)
    five_days_later = today + timezone.timedelta(days=5)
    expiring_soon = Lease.objects.filter(
        lease_end_date__range=(today, five_days_later),
        payment_status='Paid'
    )
    
    print("Expiring Leases:")
    for lease in expiring_soon:
        print(f"Lease ID: {lease.lease_id}, Tenant: {lease.tenant.tenant_name}, Warehouse: {lease.warehouse}, "
              f"Lease End Date: {lease.lease_end_date}")

        # send_mail(
        #     'Lease Expiry Notification',
        #     f'Dear {lease.tenant}, your lease for {lease.warehouse} is expiring on {lease.lease_end_date}.',
        #     'vaultspace07@gmail.com',
        #     [lease.tenant.email],
        #     fail_silently=False,
        # )
        logger.info(
            f"Notification sent to tenant {lease.tenant} for lease {lease.lease_id}. "
            f"Details: Warehouse: {lease.warehouse}, Tenant: {lease.tenant}, "
            f"Lease Start: {lease.lease_start_date}, Lease End: {lease.lease_end_date}, "
            f"Total Amount: {lease.total_amount}"
        )
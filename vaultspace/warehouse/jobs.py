from django.utils import timezone
from django.core.mail import send_mail
from .models import Lease,Warehouse
from users.models import Tenant
import logging

logger = logging.getLogger(__name__)

def send_lease_expiry_notifications_and_cleanup():
    today = timezone.now().date()
    five_days_from_now = today + timezone.timedelta(days=5)
    print(f"Today's date: {today}")
    print(f"Date five days from now: {five_days_from_now}")

    # Notify tenants whose leases are expiring within the next 5 days
    expiring_leases = Lease.objects.filter(lease_end_date__range=(today, five_days_from_now))
    
    print("Expiring Leases:")
    for lease in expiring_leases:
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
    yesterday = today - timezone.timedelta(days=1)
     # Update payment status to 'Expired' for leases that ended yesterday
    expired_leases = Lease.objects.filter(lease_end_date__lt=today, lease_end_date__gte=yesterday, payment_status='Paid')
    print("--Expired Leases:--")
    expired_leases.update(payment_status='Expired')
    for lease in expired_leases:
        lease.warehouse.status = 1
        lease.warehouse.save()
        logger.info(
            f"leases ended"
            f"Lease {lease.lease_id} status updated to 'Expired'. "
            f"Details: Warehouse: {lease.warehouse}, Tenant: {lease.tenant}, "
            f"Lease Start: {lease.lease_start_date}, Lease End: {lease.lease_end_date}, "
            f"Rental Amount: {lease.rental_amount}, Total Amount: {lease.total_amount}"
        )
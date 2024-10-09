from django import template
from users.models import Tenant
from warehouse.models import Lease

register = template.Library()

@register.simple_tag
def get_lease_info(warehouse_id):
    try:
        lease = Lease.objects.get(warehouse_id=warehouse_id)
        return {
            'lease_end_date': lease.lease_end_date,
            'tenant_name': lease.tenant.tenant_name
        }
    except Lease.DoesNotExist:
        return None
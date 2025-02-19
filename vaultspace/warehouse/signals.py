from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Warehouse, Lease, WarehouseReview

@receiver(post_save, sender=Lease)
@receiver(post_save, sender=WarehouseReview)
def update_popularity(sender, instance, **kwargs):
    warehouse = instance.warehouse
    # Simple scoring formula
    warehouse.popularity_score = (
        (warehouse.views * 0.1) +
        (warehouse.lease_set.count() * 2) +
        (warehouse.reviews.count() * 1.5) +
        (sum(r.rating for r in warehouse.reviews.all()) * 0.5)
    )
    warehouse.save()
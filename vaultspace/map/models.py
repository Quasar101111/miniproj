from django.db import models

class Location(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    nearest_main_road = models.CharField(max_length=255, blank=True, null=True)
    nearest_seaport = models.CharField(max_length=255, blank=True, null=True)
    nearest_airport = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


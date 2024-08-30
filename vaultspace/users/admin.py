# users/admin.py

from django.contrib import admin
from .models import Profile,Lessor,Tenant,Message,Payment

admin.site.register(Profile)
admin.site.register(Lessor)
admin.site.register(Tenant)
admin.site.register(Message)
admin.site.register(Payment)

# users/admin.py

from django.contrib import admin
from .models import Profile,Lessor,Tenant,Message

admin.site.register(Profile)
admin.site.register(Lessor)
admin.site.register(Tenant)
admin.site.register(Message)


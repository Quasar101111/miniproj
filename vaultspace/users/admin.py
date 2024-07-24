# users/admin.py

from django.contrib import admin
from .models import Profile,Lessor

admin.site.register(Profile)
admin.site.register(Lessor)
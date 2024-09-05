# users/admin.py

from django.contrib import admin
from .models import Profile,Lessor,Tenant,Message,Payment,ServerShare

admin.site.register(Profile)
admin.site.register(Lessor)
admin.site.register(Tenant)
admin.site.register(Message)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'lease', 'order_id', 'payment_id', 'amount', 'currency', 'status', 'created_at')  # Add created_at here
    list_filter = ('status', 'currency')  # Optional: Add filters if needed
    search_fields = ('order_id', 'payment_id', 'user__email')  # Optional: Add search fields if needed

admin.site.register(Payment, PaymentAdmin)
admin.site.register(ServerShare)
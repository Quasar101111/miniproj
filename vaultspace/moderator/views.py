# moderator/views.py

from django.shortcuts import render, redirect, get_object_or_404


from users.models import Lessor, Tenant,User
from warehouse.models import Location, Warehouse


from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.conf import settings

from django.core.mail import send_mail


def is_admin(user):
    return user.is_authenticated and user.is_superuser


# @user_passes_test(is_admin)
@login_required
def manage_tenants(request):
    tenants = Tenant.objects.all()
    user_emails = {user.email: user for user in User.objects.all()}

    tenants_with_users = []
    for tenant in tenants:
        user = user_emails.get(tenant.email)
        tenants_with_users.append({
            'tenant': tenant,
            'user': user
        })

    if request.method == 'POST':
        email = request.POST.get('email')
        action = request.POST.get('action')

        try:
            user = User.objects.get(email=email)
            if action == 'enable':
                user.is_active = True
                user.save()

                subject = 'Your account has been enabled'
                message = "Your account has been enabled. You can continue to use our services."
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [email]
                
                send_mail(subject, message, from_email, recipient_list, fail_silently=False)

                messages.success(request, f"Account for {email} has been enabled.")
            elif action == 'disable':
                user.is_active = False
                user.save()
                ban_reason = request.POST.get('ban_reason')
                
                # Send email to the tenant
                subject = 'Your account has been disabled'
                message = f"Your account has been disabled for the following reason:\n\n{ban_reason}\n\n Please contact the administrator for more information."
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [email]
                
                send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                messages.success(request, f"Account for {email} has been disabled and notified via email.")
        except User.DoesNotExist:
            messages.error(request, f"User with email {email} not found.")

        return redirect('manage_tenants')

    return render(request, 'moderator/manage_tenants.html', {'tenants_with_users': tenants_with_users})

@login_required
def manage_lessors(request):
    lessors = Lessor.objects.all()
    lessors_with_users = []
    for lessor in lessors:
        user = User.objects.filter(email=lessor.email).first()
        if user:
            lessors_with_users.append({
                'lessor': lessor,
                'user': user
            })

    if request.method == 'POST':
        email = request.POST.get('email')
        action = request.POST.get('action')

        try:
            user = User.objects.get(email=email)
            if action == 'enable':
                user.is_active = True
                user.save()
                subject = 'Your account has been enabled'
                message = "Your account has been enabled. You can continue to use our services."
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [email]
                
                send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                messages.success(request, f"Account for {email} has been enabled.")
            elif action == 'disable':
                user.is_active = False
                user.save()
                ban_reason = request.POST.get('ban_reason')
                
                # Send email to the lessor
                subject = 'Your account has been disabled'
                message = f"Your account has been disabled for the following reason:\n\n{ban_reason} \n\n Please contact the administrator for more information."
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [email]
                
                send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                messages.success(request, f"Account for {email} has been disabled and notified via email.")
        except User.DoesNotExist:
            messages.error(request, f"User with email {email} not found.")

        return redirect('manage_lessors')

    return render(request, 'moderator/manage_lessors.html', {'lessors_with_users': lessors_with_users})

@login_required
def dashboard(request):
    # Aggregate counts
    tenant_count = Tenant.objects.count()
    lessor_count = Lessor.objects.count()
    warehouse_count = Warehouse.objects.count()

    # Assuming you want to show only active warehouses
    active_warehouse_count = Warehouse.objects.filter(status=1).count()

    context = {
        'tenant_count': tenant_count,
        'lessor_count': lessor_count,
        'warehouse_count': warehouse_count,
        'active_warehouse_count': active_warehouse_count,
    }

    return render(request, 'moderator/admin_dashboard.html', context)


@login_required
def manage_warehouses(request):
    warehouses = Warehouse.objects.all().select_related('owner', 'location').order_by('-warehouse_id')

    if request.method == 'POST':
        warehouse_id = request.POST.get('warehouse_id')
        action = request.POST.get('action')

        try:
            warehouse = Warehouse.objects.get(warehouse_id=warehouse_id)
            if action == 'enable':
                warehouse.status = 1
                messages.success(request, f"Warehouse {warehouse_id} has been activated.")
            elif action == 'disable':
                warehouse.status = 2
                messages.success(request, f"Warehouse {warehouse_id} has been deactivated.")
            warehouse.save()
        except Warehouse.DoesNotExist:
            messages.error(request, f"Warehouse with ID {warehouse_id} not found.")

        return redirect('manage_warehouse')

    return render(request, 'moderator/manage_warehouse.html', {'warehouses': warehouses})




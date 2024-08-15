from django.urls import path, include
from django.conf import settings
from . import views

app_name = 'moderator'
urlpatterns = [
    # path('', views.moderator),
   path('admin_dashboard/', views.dashboard, name='admin_dashboard'),
    path('manage_lessors/', views.manage_lessors, name='manage_lessors'),
    path('manage-tenants/', views.manage_tenants, name='manage_tenants'),
    path('manage_warehouse/', views.manage_warehouses, name='manage_warehouse'),
]
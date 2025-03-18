#vaultspace/inventory/urls.py

from django.urls import path, include
from django.conf import settings
from . import views


from django.conf.urls.static import static

urlpatterns = [
	path('insert_data/<int:warehouse_id>/', views.insert_data, name='insert_data'),
    path('get-item-details/<int:item_id>/', views.get_item_details, name='get_item_details'),
    path('warehouse-dashboard/', views.warehouse_dashboard, name='warehouse_dashboard'),
    path('get-zone-items/<int:zone_id>/', views.get_zone_items, name='get_zone_items'),
    path('warehouse-data/',views. warehouse_data, name='warehouse_data'),
    path('warehouse-3d/', views.warehouse_3d_view, name='warehouse_3d'),
]
urlpatterns=urlpatterns+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
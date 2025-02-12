


from django.urls import path, include
from django.conf import settings
from . import views


from django.conf.urls.static import static

urlpatterns = [
	path('insert_data/', views.insert_data, name='insert_data'),
    path('get-item-details/<int:item_id>/', views.get_item_details, name='get_item_details'),
    path('warehouse-dashboard/', views.warehouse_dashboard, name='warehouse_dashboard'),

 
]
urlpatterns=urlpatterns+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
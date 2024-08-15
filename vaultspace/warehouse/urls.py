#warehouse/urls.py

from django.urls import path, include
from django.conf import settings
from . import views


from django.conf.urls.static import static

urlpatterns = [
	path('', views.Warehouse),	
        path('add_warehouse/', views.add_warehouse, name='add_warehouse'),
        path('temp1/', views.temp1, name='temp1'),
         path('edit_warehouse/<int:warehouse_id>/', views.edit_warehouse, name='edit_warehouse'),
       
        # path('<int:warehouse_id>/', views.warehouse_detail, name='warehouse_detail'),
]
urlpatterns=urlpatterns+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
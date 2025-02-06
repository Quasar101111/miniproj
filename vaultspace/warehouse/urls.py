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

       path('lease_warehouse/<int:warehouse_id>/', views.lease_warehouse, name='lease_warehouse'),
       path('lease_requests/', views.lease_requests, name='lease_requests'),
       path('edit_lease/<int:lease_id>/', views.edit_lease, name='edit_lease'),
      path('delete-lease/<int:lease_id>/', views.delete_lease, name='delete_lease'),
      path('termsandcond',views.termsandcond,name='termsandcond'),

      path('dashboard/', views.lessor_dashboard, name='lessor_dashboard'),
    path('revenue-chart-data/', views.revenue_chart_data, name='revenue_chart_data'),
    path('warehouse-status-chart-data/', views.warehouse_status_chart_data, name='warehouse_status_chart_data'),

     path('compare/', views.compare_warehouse, name='compare_warehouse'),

 
]
urlpatterns=urlpatterns+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
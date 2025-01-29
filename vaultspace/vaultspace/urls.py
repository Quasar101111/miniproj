"""
URL configuration for vaultspace project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from users import views as users_view
from warehouse import views as warehouse_view
from moderator import views as moderator_view
from inventory import views as inventory_view
from map import views as map_view
from django.contrib.auth import views as auth
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),

    path('accounts/', include('allauth.urls')),
    path('', include('users.urls')),
    path('login/', users_view.Login, name ='login'),
    # path('logout/', auth.LogoutView.as_view(template_name ='users/index.html'), name ='logout'),
    
    path('register_lessor/', users_view.register_lessor, name='register_lessor'),
    path('register_tenant/',users_view.register_tenant, name='register_tenant'),
     path('lessor_index/', users_view.lessor_index, name='lessor_index'),
     path('tenant_details/', users_view.tenant_details, name='tenant_details'),



    path('warehouse/', include('warehouse.urls')),
   
   
   path('view_warehouse/<int:warehouse_id>/', users_view.view_warehouse, name='view_warehouse'),
   path('warehouse_detail/<int:warehouse_id>/', users_view.warehouse_detail, name='warehouse_detail'),
   path('warehouse_list/', users_view.warehouse_list, name='warehouse_list'),

   
   
    path('add_warehouse/',warehouse_view.add_warehouse,name='add_warehouse'),
     path('edit_warehouse/<int:warehouse_id>/', warehouse_view.edit_warehouse, name='edit_warehouse'),

     path('lease-warehouse/<int:warehouse_id>/',warehouse_view.lease_warehouse, name='lease_warehouse'),
     path('lease_requests/', warehouse_view.lease_requests, name='lease_requests'),
     path('edit-lease/<int:lease_id>/', warehouse_view.edit_lease, name='edit_lease'),
     
     
     
     
     
     path('manage_tenants/', moderator_view.manage_tenants,name='manage_tenants'),
      path('manage_lessors/', moderator_view.manage_lessors,name='manage_lessors'),

      path('admin_dashboard/', moderator_view.dashboard, name='admin_dashboard'),

      path('manage_warehouse/', moderator_view.manage_warehouses, name='manage_warehouse'),


    path('payment/<int:lease_id>/', users_view.payment, name='payment'),



    path('upload-image-share/', users_view.upload_image_share, name='upload_image_share'),
    path('login-using-image/', users_view.login_using_image, name='login_using_image'),

    path('inventory/', include('inventory.urls')),

 
    path('map/', include('map.urls')),
    
]



urlpatterns=urlpatterns+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

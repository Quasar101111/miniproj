#users/urls.py

from django.urls import path, include
from django.conf import settings
from . import views

from django.contrib.auth import views as auth_views
from django.conf.urls.static import static

urlpatterns = [
		path('', views.index, name ='index'),
        path('logout/', views.Logout, name='logout'),
        path('login/', views.Login, name='login'),

        path('register_lessor/', views.register_lessor, name='register_lessor'),
    	path('register_tenant/', views.register_tenant, name='register_tenant'),
        path('lessor_details/', views.lessor_details, name='lessor_details'),
        path('lessor_index/', views.lessor_index, name='lessor_index'),
        path('tenant_details/', views.tenant_details, name='tenant_details'),
        path('temp/', views.temp, name='temp'),  
        
        path('view_warehouse/<int:warehouse_id>/', views.view_warehouse, name='view_warehouse'),
        path('warehouse_list/', views.warehouse_list, name='warehouse_list'),
        path('warehouse_detail/<int:warehouse_id>/', views.warehouse_detail, name='warehouse_detail'),


        path('verify-otp/', views.verify_otp, name='verify_otp'),


        # Password reset URLs
        path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
        path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ), name='password_reset_done'),
        path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html'
        ), name='password_reset_confirm'),
        path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ), name='password_reset_complete'),
        
        
    #message  

        path('lessor-messages/', views.lessor_messages, name='lessor_messages'),
        path('tenant-messages/', views.tenant_messages, name='tenant_messages'),
        
  

        path('message_detail/<str:recipient_email>/', views.message_detail, name='message_detail'),
        path('message_detail/<str:recipient_email>/get/', views.get_messages, name='get_messages'),


    #lease 

        path('lease_offers/', views.lease_offers, name='lease_offers'),
        path('rented_warehouses/',views.rented_warehouses, name='rented_warehouses'),

        path('payment/<int:lease_id>/', views.payment, name='payment'),
        path('payment_result/<int:lease_id>/', views.payment_result, name='payment_result'),



    ]

#users/urls.py

from django.urls import path, include
from django.conf import settings
from . import views

from django.contrib.auth import views as auth_views
from django.conf.urls.static import static

urlpatterns = [
		path('', views.index, name ='index'),
        path('logout/', views.Logout, name='logout'),
        path('register_lessor/', views.register_lessor, name='register_lessor'),
    	path('register_tenant/', views.register_tenant, name='register_tenant'),
        path('lessor_details/', views.lessor_details, name='lessor_details'),
     
]

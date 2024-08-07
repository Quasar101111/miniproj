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
    path('warehouse/', include('warehouse.urls')),
    path('add_warehouse/',warehouse_view.add_warehouse,name='add_warehouse'),
     path('edit_warehouse/<int:warehouse_id>/', warehouse_view.edit_warehouse, name='edit_warehouse'),

    
]
urlpatterns=urlpatterns+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

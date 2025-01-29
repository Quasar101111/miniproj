


from django.urls import path, include
from django.conf import settings
from . import views


from django.conf.urls.static import static

urlpatterns = [
	path('insert_data/', views.insert_data, name='insert_data'),

 
]
urlpatterns=urlpatterns+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
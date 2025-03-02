# sistemakq/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('kq_app.urls')),  # Inclui as URLs do aplicativo kq_app
]
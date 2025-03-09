"""
URL Configuration for ratingproject
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('ratingapi.urls')),
    path('', include('ratingapi.urls')), 
]

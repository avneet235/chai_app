from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home),
    path('about/', views.about),
    path('contact/', views.contact),
    path('chai/', include('chai.urls')),
    
    
    
    path("__reload__/", include("django_browser_reload.urls")),
]

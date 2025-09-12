from django.urls import path, include
from . import views

urlpatterns = [
    path('auth/', include('apps.api_auth.urls')),

]

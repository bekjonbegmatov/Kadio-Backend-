from django.urls import path
from . import views

urlpatterns = [
    path('user/', views.UserActivityView.as_view()),
]
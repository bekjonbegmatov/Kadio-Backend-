from django.urls import path, include
from . import views

urlpatterns = [
    path('auth/', include('apps.api_auth.urls')),
    path('activitys/', include('apps.user_activitys.urls')),
    
    # friendships
    path('friends/add/', views.FriendshipViewSet.as_view()),
]

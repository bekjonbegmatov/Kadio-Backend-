from django.urls import path, include
from . import views

urlpatterns = [
    path('auth/', include('apps.api_auth.urls')),
    path('activitys/', include('apps.user_activitys.urls')),
    path('game/', include('apps.gamedification.urls')),
    
    # friendships
    path('friends/add/', views.FriendshipViewSet.as_view()),
    path('friends/', views.UserFrendsView.as_view()),
    path('friends/recommendations/', views.UserFrensReomendationView.as_view()),
    path('friends/requests/', views.UserFrensRequests.as_view()),
    path('friends/search/', views.UserSearchView.as_view()),
    
]

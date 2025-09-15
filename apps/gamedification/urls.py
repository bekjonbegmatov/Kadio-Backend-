from django.urls import path
from . import views

urlpatterns = [
    path('leaderboard/global/', views.LiderboardView.as_view()),
    path('leaderboard/frends/', views.UserFrendsLiderboardView.as_view()),
]

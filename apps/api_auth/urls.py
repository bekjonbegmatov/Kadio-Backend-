from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
 
    path('all/', views.get_all_users, name='all'),
    
    # Защищенные эндпоинты (требуют токен)
    path('profile/', views.get_user_profile, name='user_profile'),
    path('profile/ /', views.update_user_profile, name='update_user_profile'),
    path('profile/upload-avatar/', views.upload_avatar, name='upload_avatar'),
]
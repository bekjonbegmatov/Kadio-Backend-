from django.urls import path
from . import views

app_name = 'feed'

urlpatterns = [
    # Посты
    path('posts/', views.PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    
    # Комментарии
    path('posts/<int:post_id>/comments/', views.CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', views.CommentDetailView.as_view(), name='comment-detail'),
    
    # Лайки
    path('posts/<int:post_id>/like/', views.toggle_like, name='toggle-like'),
    
    # Поиск
    path('search/', views.search_posts, name='search-posts'),
    
    # Рекомендации
    path('recommendations/', views.get_recommendations, name='recommendations'),
    
    # Посты пользователя
    path('my-posts/', views.get_user_posts, name='my-posts'),
    path('users/<int:user_id>/posts/', views.get_user_posts, name='user-posts'),
]
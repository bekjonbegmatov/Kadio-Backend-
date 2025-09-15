from rest_framework import generics, status, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count, Case, When, IntegerField
from django.utils import timezone
from django.http import Http404
from apps.api_auth.decorators import token_required
from .models import Post, Comment, Like, PostView, PostRecommendation
from .serializers import (
    PostListSerializer, PostDetailSerializer, PostCreateUpdateSerializer,
    CommentSerializer, LikeSerializer, PostSearchSerializer,
    PostRecommendationSerializer
)
from .utils import RecommendationEngine


class PostPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class PostListCreateView(generics.ListCreateAPIView):
    """
    Список постов и создание нового поста
    """
    pagination_class = PostPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'likes_count', 'views_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Post.objects.filter(is_published=True).select_related('author')
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateUpdateSerializer
        return PostListSerializer
    
    @token_required
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    



class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Детальный просмотр, обновление и удаление поста
    """
    queryset = Post.objects.all().select_related('author')
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PostCreateUpdateSerializer
        return PostDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Записываем просмотр
        self.record_view(instance, request)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def record_view(self, post, request):
        """
        Записывает просмотр поста
        """
        user = getattr(request, 'user', None)
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Проверяем, не было ли уже просмотра от этого пользователя/IP за последний час
        one_hour_ago = timezone.now() - timezone.timedelta(hours=1)
        
        if user:
            existing_view = PostView.objects.filter(
                post=post, user=user, viewed_at__gte=one_hour_ago
            ).exists()
        else:
            existing_view = PostView.objects.filter(
                post=post, ip_address=ip_address, viewed_at__gte=one_hour_ago
            ).exists()
        
        if not existing_view:
            PostView.objects.create(
                post=post,
                user=user,
                ip_address=ip_address,
                user_agent=user_agent
            )
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @token_required
    def put(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return Response(
                {'error': 'У вас нет прав для редактирования этого поста'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().put(request, *args, **kwargs)
    
    @token_required
    def patch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return Response(
                {'error': 'У вас нет прав для редактирования этого поста'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().patch(request, *args, **kwargs)
    
    @token_required
    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return Response(
                {'error': 'У вас нет прав для удаления этого поста'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().delete(request, *args, **kwargs)


class CommentListCreateView(generics.ListCreateAPIView):
    """
    Список комментариев к посту и создание нового комментария
    """
    serializer_class = CommentSerializer
    pagination_class = PostPagination
    
    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Comment.objects.filter(
            post_id=post_id, parent=None
        ).select_related('author').order_by('created_at')
    
    @token_required
    def post(self, request, *args, **kwargs):
        post_id = self.kwargs['post_id']
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(
                {'error': 'Пост не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Детальный просмотр, обновление и удаление комментария
    """
    queryset = Comment.objects.all().select_related('author')
    serializer_class = CommentSerializer
    
    @token_required
    def put(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            return Response(
                {'error': 'У вас нет прав для редактирования этого комментария'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().put(request, *args, **kwargs)
    
    @token_required
    def patch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            return Response(
                {'error': 'У вас нет прав для редактирования этого комментария'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().patch(request, *args, **kwargs)
    
    @token_required
    def delete(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            return Response(
                {'error': 'У вас нет прав для удаления этого комментария'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().delete(request, *args, **kwargs)


@api_view(['POST', 'DELETE'])
@token_required
def toggle_like(request, post_id):
    """
    Поставить или убрать лайк с поста
    """
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response(
            {'error': 'Пост не найден'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    like, created = Like.objects.get_or_create(
        post=post,
        user=request.user
    )
    
    if request.method == 'POST':
        if created:
            return Response(
                {'message': 'Лайк поставлен', 'liked': True},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'message': 'Лайк уже поставлен', 'liked': True},
                status=status.HTTP_200_OK
            )
    
    elif request.method == 'DELETE':
        if not created:
            like.delete()
            return Response(
                {'message': 'Лайк убран', 'liked': False},
                status=status.HTTP_200_OK
            )
        else:
            like.delete()  # Удаляем только что созданный лайк
            return Response(
                {'message': 'Лайк не был поставлен', 'liked': False},
                status=status.HTTP_200_OK
            )


@api_view(['GET'])
def search_posts(request):
    """
    Поиск постов по различным критериям
    """
    serializer = PostSearchSerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    queryset = Post.objects.filter(is_published=True).select_related('author').annotate(
        likes_count=Count('likes'),
        comments_count=Count('comments'),
        views_count=Count('views')
    )
    
    # Поиск по тексту
    if data.get('query'):
        query = data['query']
        queryset = queryset.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
    
    # Поиск по тегам
    if data.get('tags'):
        for tag in data['tags']:
            queryset = queryset.filter(tags__contains=[tag])
    
    # Поиск по автору
    if data.get('author'):
        author = data['author']
        queryset = queryset.filter(
            Q(author__username__icontains=author) | 
            Q(author__full_name__icontains=author)
        )
    
    # Фильтр по дате
    if data.get('date_from'):
        queryset = queryset.filter(created_at__gte=data['date_from'])
    
    if data.get('date_to'):
        queryset = queryset.filter(created_at__lte=data['date_to'])
    
    # Сортировка
    ordering = data.get('ordering', '-created_at')
    if ordering in ['-likes_count', '-views_count']:
        queryset = queryset.order_by(ordering, '-created_at')
    else:
        queryset = queryset.order_by(ordering)
    
    # Пагинация
    paginator = PostPagination()
    page = paginator.paginate_queryset(queryset, request)
    if page is not None:
        serializer = PostListSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
    serializer = PostListSerializer(queryset, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@token_required
def get_recommendations(request):
    """
    Получить рекомендованные посты для пользователя
    """
    engine = RecommendationEngine()
    recommendations = engine.get_recommendations_for_user(request.user)
    
    paginator = PostPagination()
    page = paginator.paginate_queryset(recommendations, request)
    if page is not None:
        serializer = PostRecommendationSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
    serializer = PostRecommendationSerializer(recommendations, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@token_required
def get_user_posts(request, user_id=None):
    """
    Получить посты пользователя
    """
    if user_id:
        try:
            from apps.api_auth.models import UserModel
            user = UserModel.objects.get(id=user_id)
        except UserModel.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        user = request.user
    
    queryset = Post.objects.filter(
        author=user, is_published=True
    ).select_related('author').annotate(
        likes_count=Count('likes'),
        comments_count=Count('comments'),
        views_count=Count('views')
    ).order_by('-created_at')
    
    paginator = PostPagination()
    page = paginator.paginate_queryset(queryset, request)
    if page is not None:
        serializer = PostListSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
    serializer = PostListSerializer(queryset, many=True, context={'request': request})
    return Response(serializer.data)

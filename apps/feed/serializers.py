from rest_framework import serializers
from .models import Post, Comment, Like, PostView, PostRecommendation
from apps.api_auth.models import UserModel


class UserBasicSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор пользователя для отображения в постах и комментариях
    """
    class Meta:
        model = UserModel
        fields = ['id', 'username', 'full_name', 'avatar', 'level']
        read_only_fields = ['id', 'username', 'full_name', 'avatar', 'level']


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для комментариев
    """
    author = UserBasicSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'author', 'parent', 'content', 
            'created_at', 'updated_at', 'replies', 'replies_count'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
    
    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True, context=self.context).data
        return []
    
    def get_replies_count(self, obj):
        return obj.replies.count()
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class LikeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для лайков
    """
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'post', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PostListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка постов (краткая информация)
    """
    author = UserBasicSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    views_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    content_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content_preview', 'image', 'tags', 
            'author', 'likes_count', 'comments_count', 'views_count',
            'is_liked', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'author', 'likes_count', 'comments_count', 
            'views_count', 'created_at', 'updated_at'
        ]
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user and request.user.is_authenticated:
            return Like.objects.filter(post=obj, user=request.user).exists()
        return False
    
    def get_likes_count(self, obj):
        return obj.likes_count
    
    def get_comments_count(self, obj):
        return obj.comments_count
    
    def get_views_count(self, obj):
        return obj.views_count
    
    def get_content_preview(self, obj):
        # Возвращаем первые 200 символов контента
        return obj.content[:200] + '...' if len(obj.content) > 200 else obj.content


class PostDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для детального просмотра поста
    """
    author = UserBasicSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    views_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'image', 'tags', 'author',
            'likes_count', 'comments_count', 'views_count', 'is_liked',
            'comments', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'author', 'likes_count', 'comments_count', 
            'views_count', 'created_at', 'updated_at'
        ]
    
    def get_likes_count(self, obj):
        return obj.likes_count
    
    def get_comments_count(self, obj):
        return obj.comments_count
    
    def get_views_count(self, obj):
        return obj.views_count
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user and request.user.is_authenticated:
            return Like.objects.filter(post=obj, user=request.user).exists()
        return False
    
    def get_comments(self, obj):
        # Получаем только комментарии верхнего уровня (без родителя)
        top_level_comments = obj.comments.filter(parent=None).order_by('created_at')
        return CommentSerializer(top_level_comments, many=True, context=self.context).data


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления постов
    """
    is_published = serializers.BooleanField(default=True)
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'tags', 'is_published']
    
    def validate_content(self, value):
        if len(value) > 4000:
            raise serializers.ValidationError("Содержание поста не может превышать 4000 символов.")
        return value
    
    def validate_tags(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Теги должны быть списком.")
        if len(value) > 10:
            raise serializers.ValidationError("Максимальное количество тегов: 10.")
        return value
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class PostViewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для просмотров постов
    """
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = PostView
        fields = ['id', 'post', 'user', 'ip_address', 'viewed_at']
        read_only_fields = ['id', 'user', 'ip_address', 'viewed_at']


class PostRecommendationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для рекомендаций постов
    """
    post = PostListSerializer(read_only=True)
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = PostRecommendation
        fields = ['id', 'user', 'post', 'score', 'reason', 'created_at']
        read_only_fields = ['id', 'user', 'post', 'score', 'reason', 'created_at']


class PostSearchSerializer(serializers.Serializer):
    """
    Сериализатор для поиска постов
    """
    query = serializers.CharField(max_length=255, required=False, allow_blank=True)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        allow_empty=True
    )
    author = serializers.CharField(max_length=255, required=False, allow_blank=True)
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    ordering = serializers.ChoiceField(
        choices=['-created_at', 'created_at', '-likes_count', '-views_count'],
        default='-created_at'
    )
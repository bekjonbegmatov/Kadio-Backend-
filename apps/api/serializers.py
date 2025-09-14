from rest_framework import serializers
from .models import Friendship
from apps.api_auth.models import UserModel

class UserBasicSerializer(serializers.ModelSerializer):
    """Базовый сериализатор пользователя без токена"""
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UserModel
        fields = [
            'id', 'username', 'full_name', 'avatar_url', 'bio', 
            'level', 'interests', 'created', 'date_of_birth', 'user_time_zone', 'last_active'
        ]
    
    def get_avatar_url(self, obj):
        """Возвращает полный URL аватарки пользователя"""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None

class FriendshipSerializer(serializers.ModelSerializer):
    from_user = UserBasicSerializer(read_only=True)
    to_user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Friendship
        fields = ["from_user", "to_user", "status", "created_at"]
        read_only_fields = ["created_at"]

class UserRecommendationSerializer(serializers.ModelSerializer):
    """Сериализатор для рекомендаций пользователей"""
    avatar_url = serializers.SerializerMethodField()
    recommendation_score = serializers.FloatField(read_only=True)
    recommendation_reasons = serializers.ListField(read_only=True)
    mutual_friends_count = serializers.IntegerField(read_only=True)
    common_interests = serializers.ListField(read_only=True)
    
    class Meta:
        model = UserModel
        fields = [
            'id', 'username', 'full_name', 'avatar', 'avatar_url', 'bio', 
            'level', 'interests', 'recommendation_score', 'recommendation_reasons',
            'mutual_friends_count', 'common_interests'
        ]
        extra_kwargs = {'avatar': {'write_only': True}}
    
    def get_avatar_url(self, obj):
        """Возвращает полный URL аватарки пользователя"""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None
    
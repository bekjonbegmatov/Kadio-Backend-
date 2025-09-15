from rest_framework import serializers
from .models import ChatRoom, Message
from apps.api_auth.models import UserModel


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'username', 'email', 'avatar', 'full_name']


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'content', 'timestamp', 'is_read', 'sender']
        read_only_fields = ['id', 'timestamp', 'sender']


class ChatRoomSerializer(serializers.ModelSerializer):
    user1 = UserSerializer(read_only=True)
    user2 = UserSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    other_user = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'user1', 'user2', 'created_at', 'updated_at', 'last_message', 'unread_count', 'other_user']
    
    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return MessageSerializer(last_message).data
        return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            # Считаем непрочитанные сообщения для текущего пользователя
            other_user = obj.get_other_user(request.user)
            return obj.messages.filter(sender=other_user, is_read=False).count()
        return 0
    
    def get_other_user(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            other_user = obj.get_other_user(request.user)
            return UserSerializer(other_user).data
        return None


class FriendSerializer(serializers.ModelSerializer):
    """Сериализатор для списка друзей"""
    class Meta:
        model = UserModel
        fields = ['id', 'username', 'email', 'avatar', 'full_name', 'last_active']
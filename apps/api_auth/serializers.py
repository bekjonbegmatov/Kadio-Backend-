from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import UserModel

class UserAuthSerializer(ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'username', 'email', 'password', 'token']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = UserModel(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        user.generate_token()  
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'token': user.token
        }

class UserSerializer(ModelSerializer):
    avatar_url = SerializerMethodField()
    
    class Meta:
        model = UserModel
        fields = ['id', 'username', 'email', 'streak_days', 'level', 'interests', 'avatar', 'avatar_url', 'bio', 'user_time_zone', 'last_active', 'full_name', 'link', 'date_of_birth', 'diamonds', 'coins']
        extra_kwargs = {'avatar': {'write_only': True}}
    
    def get_avatar_url(self, obj):
        """Возвращает полный URL аватарки пользователя"""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None
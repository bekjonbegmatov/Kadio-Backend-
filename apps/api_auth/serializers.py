from rest_framework.serializers import ModelSerializer
from .models import UserModel

class UserAuthSerializer(ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = UserModel(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        user.generate_token()  
        return {
            'username': user.username,
            'email': user.email,
            'token': user.token
        }

class UserSerializer(ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['username', 'email', 'streak_days', 'level', 'interests', 'avatar', 'bio', 'user_time_zone', 'last_active']
from rest_framework import serializers
from .models import UserActivity, Badge, UserNotifications

class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = '__all__'
        
class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = '__all__'

class UserNotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotifications
        fields = '__all__'

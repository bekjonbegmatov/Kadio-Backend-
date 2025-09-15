from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import serializers
from django.utils import timezone
from .models import GiveawayModel


class GiveawaySerializer(ModelSerializer):
    participants_count = SerializerMethodField()
    time_left = SerializerMethodField()
    organizator_email = SerializerMethodField()
    
    class Meta:
        model = GiveawayModel
        fields = '__all__'
        read_only_fields = ('organizator', 'participants', 'winner', 'created_at', 'updated_at')
    
    def get_participants_count(self, obj):
        return obj.participants.count()
    
    def get_time_left(self, obj):
        if obj.end_date > timezone.now():
            delta = obj.end_date - timezone.now()
            return {
                'days': delta.days,
                'hours': delta.seconds // 3600,
                'minutes': (delta.seconds % 3600) // 60
            }
        return None
    
    def get_organizator_email(self, obj):
        return obj.organizator.email if obj.organizator else None
    
    def validate(self, data):
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError("End date must be after start date")
        
        if data.get('giveaway_cost', 0) < 0:
            raise serializers.ValidationError("Giveaway cost cannot be negative")
        
        if data.get('prize_fond', 0) < 0:
            raise serializers.ValidationError("Prize fund cannot be negative")
        
        return data
        
    
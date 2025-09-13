from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import UserActivity
from .serializers import UserActivitySerializer

from apps.api_auth.decorators import token_required

class UserActivityView(APIView):
    @token_required
    def get(self, request):
        user = request.user
        activities = user.activities.filter(timestamp__month=timezone.now().month).order_by('-timestamp')
        serializer = UserActivitySerializer(activities, many=True)
        return Response(serializer.data)
    
    @token_required
    def post(self, request):
        user = request.user
        action = request.data.get('action')
        timestamp = request.data.get('timestamp', timezone.now())
        if not action:
            return Response({'error': 'Action is required'}, status=400)
        activity = UserActivity(user=user, action=action, timestamp=timestamp)
        activity.save()
        serializer = UserActivitySerializer(activity)
        return Response(serializer.data, status=201)
    
from django.http import HttpResponse

def index(request):

    return HttpResponse("Hello, world. You're at the api index.")


from rest_framework.views import APIView
from .models import Friendship
from .serializers import FriendshipSerializer

from apps.api_auth.decorators import token_required
from apps.api_auth.models import UserModel
from rest_framework.response import Response
from rest_framework import status


class FriendshipViewSet(APIView):
    
    @token_required
    def post(self,request):
        from_user = request.user
        
        to_user_id = request.data.get("to_user")
        if not to_user_id:
            return Response({"error": "to_user field is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            to_user_id = int(to_user_id)
        except (ValueError, TypeError):
            return Response({"error": "Invalid user ID format"}, status=status.HTTP_400_BAD_REQUEST)
        
        to_user = UserModel.objects.filter(id=to_user_id).first()
        if not to_user:
            return Response({"error": f"User not found with id {to_user_id}"}, status=status.HTTP_404_NOT_FOUND)
        
        # Проверяем, что пользователь не добавляет себя в друзья
        if from_user.id == to_user.id:
            return Response({"error": "You cannot add yourself as a friend"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Проверяем, не существует ли уже заявка в дружбу
        existing_friendship = Friendship.objects.filter(
            from_user=from_user, 
            to_user=to_user
        ).first()
        
        if existing_friendship:
            return Response({
                "error": f"Friendship request already exists with status: {existing_friendship.status}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        friendship = Friendship.objects.create(
            from_user=from_user,
            to_user=to_user,
            status="pending"
        )
        
        serializer = FriendshipSerializer(friendship)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


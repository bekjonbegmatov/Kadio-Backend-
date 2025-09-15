from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.api_auth.models import UserModel
from apps.api.models import Friendship

from apps.api_auth.decorators import token_required

class LiderboardView(APIView):
    def get(self, request):
        users_limit = request.query_params.get('limit', 10)
        try:
            users_limit = int(users_limit)
        except ValueError:
            users_limit = 10
            
        users = UserModel.objects.all().order_by('-coins')[:users_limit]
        response_data = [
            {
                "id": user.id,
                "email": user.email,
                "diamonds": user.diamonds,
                "coins": user.coins,
                "avatar": user.avatar.url if user.avatar else None,
            }
            for user in users
        ]
        
        return Response(response_data, status=status.HTTP_200_OK)

class UserFrendsLiderboardView(APIView):
    @token_required
    def get(self, request):
        user = request.user
        
        # Получаем друзей пользователя (принятые заявки в дружбу)
        sent_friendships = user.friendship_requests_sent.filter(status='accepted')
        received_friendships = user.friendship_requests_received.filter(status='accepted')
        
        # Собираем всех друзей
        friends = []
        for friendship in sent_friendships:
            friends.append(friendship.to_user)
        for friendship in received_friendships:
            friends.append(friendship.from_user)
        friends.append(user)
        # Сортируем друзей по уровню (по убыванию)
        friends_sorted = sorted(friends, key=lambda friend: friend.level, reverse=True)
        
        # Формируем ответ
        response_data = [
            {
                "id": user.id,
                "email": user.email,
                "diamonds": user.diamonds,
                "coins": user.coins,
                "avatar": user.avatar.url if user.avatar else None,
            }
            for user in friends_sorted
        ]
        
        return Response(response_data, status=status.HTTP_200_OK)
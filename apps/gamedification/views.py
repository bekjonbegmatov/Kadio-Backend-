from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from apps.api_auth.models import UserModel
from apps.api.models import Friendship
from .models import GiveawayModel
from .serializers import GiveawaySerializer

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
    
    
class GiveawaysView(APIView):
    
    def get(self, request):
        # Показываем только активные конкурсы, которые еще не закончились
        giveaways = GiveawayModel.objects.filter(
            is_active=True,
            end_date__gt=timezone.now()
        ).order_by('-created_at')
        serializer = GiveawaySerializer(giveaways, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @token_required
    def post(self, request):
        serializer = GiveawaySerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            prize_fond = serializer.validated_data['prize_fond']
            
            # Проверяем, достаточно ли diamonds у организатора
            if user.diamonds < prize_fond:
                return Response(
                    {"error": "You don't have enough diamonds to create this giveaway"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Списываем diamonds с баланса организатора
            user.diamonds -= prize_fond
            user.save()
            
            # Устанавливаем текущего пользователя как организатора
            serializer.save(organizator=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class GiveawayView(APIView):
    def get(self, request, pk):
        try:
            giveaway = GiveawayModel.objects.get(id=pk)
        except GiveawayModel.DoesNotExist:
            return Response({"error": "Giveaway not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = GiveawaySerializer(giveaway)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @token_required    
    def post(self, request, pk):
        try:
            giveaway = GiveawayModel.objects.get(id=pk)
        except GiveawayModel.DoesNotExist:
            return Response({"error": "Giveaway not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Проверяем, активен ли конкурс и не закончился ли он
        if not giveaway.is_active:
            return Response({"error": "This giveaway is not active"}, status=status.HTTP_400_BAD_REQUEST)
        
        if giveaway.end_date <= timezone.now():
            return Response({"error": "This giveaway has ended"}, status=status.HTTP_400_BAD_REQUEST)
        
        if giveaway.start_date > timezone.now():
            return Response({"error": "This giveaway has not started yet"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        if user in giveaway.participants.all():
            return Response({"error": "You already participated in this giveaway"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Проверяем, достаточно ли у пользователя diamonds
        if user.diamonds < giveaway.giveaway_cost:
            return Response({"error": "You don't have enough diamonds to participate"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Списываем diamonds и добавляем участника
        user.diamonds -= giveaway.giveaway_cost
        user.save()
        giveaway.participants.add(user)
        
        # Добавляем стоимость участия к призовому фонду
        giveaway.add_sum(giveaway.giveaway_cost)
        
        # Возвращаем обновленную информацию о конкурсе
        serializer = GiveawaySerializer(giveaway)
        return Response({
            "message": "Successfully participated in giveaway",
            "giveaway": serializer.data
        }, status=status.HTTP_200_OK)
    
    
    
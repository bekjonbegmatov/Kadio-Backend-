from django.http import HttpResponse

def index(request):

    return HttpResponse("Hello, world. You're at the api index.")


from rest_framework.views import APIView
from .models import Friendship
from .serializers import FriendshipSerializer, UserRecommendationSerializer

from apps.api_auth.decorators import token_required
from apps.api_auth.models import UserModel
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q
from collections import defaultdict
import random


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
        
        # Проверка о том что есть ли заявка от пользователя to_user к from_user
        existing_friendship = Friendship.objects.filter(
            from_user=to_user, 
            to_user=from_user
        ).first()
        if existing_friendship:
            if existing_friendship.status == "pending":
                existing_friendship.status = "accepted"
                existing_friendship.save()
                return Response({
                    "message": f"Friendship request from {to_user.username} to {from_user.username} has been accepted"
                }, status=status.HTTP_200_OK)
        
        friendship = Friendship.objects.create(
            from_user=from_user,
            to_user=to_user,
            status="pending"
        )
        
        serializer = FriendshipSerializer(friendship)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserFrendsView(APIView):
    @token_required
    def get(self, request):
        user = request.user
        friendships = Friendship.objects.filter(
            Q(from_user=user) | Q(to_user=user)
        )
        serializer = FriendshipSerializer(friendships, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UserFrensRequests(APIView):
    @token_required
    def get(self, request):
        user = request.user
        
        # Входящие запросы (кто отправил запрос текущему пользователю)
        incoming_requests = Friendship.objects.filter(
            Q(to_user=user) & Q(status="pending")
        )
        
        # Исходящие запросы (кому текущий пользователь отправил запрос)
        outgoing_requests = Friendship.objects.filter(
            Q(from_user=user) & Q(status="pending")
        )
        
        incoming_serializer = FriendshipSerializer(incoming_requests, many=True)
        outgoing_serializer = FriendshipSerializer(outgoing_requests, many=True)
        
        response_data = {
            "incoming_requests": incoming_serializer.data,
            "outgoing_requests": outgoing_serializer.data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
class UserFrensReomendationView(APIView):
    @token_required
    def get(self, request):
        user = request.user
        limit = int(request.GET.get('limit', 10))  # Лимит рекомендаций
        
        # Получаем всех друзей пользователя (принятые заявки)
        user_friends = self._get_user_friends(user)
        user_friend_ids = [friend.id for friend in user_friends]
        
        # Получаем всех пользователей, исключая текущего и его друзей
        potential_friends = UserModel.objects.exclude(
            Q(id=user.id) | Q(id__in=user_friend_ids)
        ).filter(is_active=True)
        
        # Исключаем пользователей с которыми уже есть заявки в дружбу
        existing_requests = Friendship.objects.filter(
            Q(from_user=user) | Q(to_user=user)
        ).values_list('from_user_id', 'to_user_id')
        
        excluded_ids = set()
        for from_id, to_id in existing_requests:
            if from_id != user.id:
                excluded_ids.add(from_id)
            if to_id != user.id:
                excluded_ids.add(to_id)
        
        potential_friends = potential_friends.exclude(id__in=excluded_ids)
        
        # Вычисляем рекомендации для каждого потенциального друга
        recommendations = []
        for potential_friend in potential_friends:
            score_data = self._calculate_recommendation_score(
                user, potential_friend, user_friends
            )
            if score_data['score'] > 0:  # Только если есть хоть какая-то связь
                # Добавляем дополнительные поля к объекту пользователя
                potential_friend.recommendation_score = score_data['score']
                potential_friend.recommendation_reasons = score_data['reasons']
                potential_friend.mutual_friends_count = score_data['mutual_friends_count']
                potential_friend.common_interests = score_data['common_interests']
                recommendations.append(potential_friend)
        
        # Сортируем по скору и добавляем случайность для равных скоров
        recommendations.sort(key=lambda x: (x.recommendation_score, random.random()), reverse=True)
        
        # Ограничиваем количество рекомендаций
        recommendations = recommendations[:limit]
        
        # Сериализуем результат
        serializer = UserRecommendationSerializer(
            recommendations, many=True, context={'request': request}
        )
        
        return Response({
            'recommendations': serializer.data,
            'total_count': len(recommendations),
            'algorithm_version': '1.0'
        }, status=status.HTTP_200_OK)
    
    def _get_user_friends(self, user):
        """Получает всех друзей пользователя (принятые заявки)"""
        friend_relationships = Friendship.objects.filter(
            Q(from_user=user, status='accepted') | Q(to_user=user, status='accepted')
        )
        
        friends = []
        for relationship in friend_relationships:
            if relationship.from_user == user:
                friends.append(relationship.to_user)
            else:
                friends.append(relationship.from_user)
        
        return friends
    
    def _calculate_recommendation_score(self, user, potential_friend, user_friends):
        """Вычисляет скор рекомендации для потенциального друга"""
        score = 0
        reasons = []
        common_interests = []
        mutual_friends_count = 0
        
        # 1. Анализ общих интересов
        if user.interests and potential_friend.interests:
            user_interests = self._extract_interests(user.interests)
            friend_interests = self._extract_interests(potential_friend.interests)
            
            common = set(user_interests) & set(friend_interests)
            if common:
                common_interests = list(common)
                interest_score = len(common) * 2  # 2 балла за каждый общий интерес
                score += interest_score
                reasons.append(f"Общие интересы: {', '.join(list(common)[:3])}{'...' if len(common) > 3 else ''}")
        
        # 2. Анализ взаимных друзей (друзья друзей)
        potential_friend_friends = self._get_user_friends(potential_friend)
        mutual_friends = set(friend.id for friend in user_friends) & set(friend.id for friend in potential_friend_friends)
        
        if mutual_friends:
            mutual_friends_count = len(mutual_friends)
            mutual_score = len(mutual_friends) * 3  # 3 балла за каждого взаимного друга
            score += mutual_score
            
            if len(mutual_friends) == 1:
                reasons.append("1 общий друг")
            else:
                reasons.append(f"{len(mutual_friends)} общих друзей")
        
        # 3. Бонус за активность (уровень пользователя)
        if potential_friend.level > 0:
            level_bonus = min(potential_friend.level * 0.5, 5)  # Максимум 5 баллов
            score += level_bonus
            if potential_friend.level >= 10:
                reasons.append(f"Активный пользователь (уровень {potential_friend.level})")
        
        # 4. Небольшой случайный фактор для разнообразия
        if score > 0:
            score += random.uniform(0, 1)
        
        # 5. Если нет явных связей, но пользователь активен - минимальный скор
        if score == 0 and potential_friend.level > 0:
            score = 0.1
            reasons.append("Новый пользователь")
        
        return {
            'score': round(score, 2),
            'reasons': reasons,
            'common_interests': common_interests,
            'mutual_friends_count': mutual_friends_count
        }
    
    def _extract_interests(self, interests_data):
        """Извлекает список интересов из JSON поля"""
        if isinstance(interests_data, dict):
            all_interests = []
            for category, items in interests_data.items():
                if isinstance(items, list):
                    all_interests.extend([item.lower().strip() for item in items if item])
                elif isinstance(items, str):
                    all_interests.append(items.lower().strip())
            return all_interests
        elif isinstance(interests_data, list):
            return [item.lower().strip() for item in interests_data if item]
        return []
        
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from apps.api_auth.decorators import token_required
from apps.api_auth.models import UserModel
from apps.api.models import Friendship
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer, FriendSerializer


class FriendsListView(APIView):
    """Получение списка друзей для чата"""
    
    @token_required
    def get(self, request):
        user = request.user
        
        # Получаем всех друзей (принятые заявки)
        friendships = Friendship.objects.filter(
            Q(from_user=user, status='accepted') | Q(to_user=user, status='accepted')
        )
        
        friends = []
        for friendship in friendships:
            if friendship.from_user == user:
                friends.append(friendship.to_user)
            else:
                friends.append(friendship.from_user)
        
        serializer = FriendSerializer(friends, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChatRoomListView(APIView):
    """Получение списка чат-комнат пользователя"""
    
    @token_required
    def get(self, request):
        user = request.user
        
        # Получаем все чат-комнаты пользователя
        chat_rooms = ChatRoom.objects.filter(
            Q(user1=user) | Q(user2=user)
        ).order_by('-updated_at')
        
        serializer = ChatRoomSerializer(chat_rooms, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChatRoomDetailView(APIView):
    """Получение или создание чат-комнаты с другом"""
    
    @token_required
    def get(self, request, friend_id):
        user = request.user
        
        try:
            friend = UserModel.objects.get(id=friend_id)
        except UserModel.DoesNotExist:
            return Response(
                {'error': 'Friend not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            # Получаем или создаем комнату
            room, created = ChatRoom.get_or_create_room(user, friend)
            serializer = ChatRoomSerializer(room, context={'request': request})
            
            return Response({
                'room': serializer.data,
                'created': created
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_403_FORBIDDEN
            )


class ChatMessagesView(APIView):
    """Получение сообщений чата"""
    
    @token_required
    def get(self, request, room_id):
        user = request.user
        
        try:
            room = ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            return Response(
                {'error': 'Chat room not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Проверяем доступ к комнате
        if user != room.user1 and user != room.user2:
            return Response(
                {'error': 'Access denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Получаем параметры пагинации
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 50))
        
        # Получаем сообщения с пагинацией
        messages = room.messages.all()[(page-1)*page_size:page*page_size]
        
        # Отмечаем сообщения как прочитанные
        unread_messages = room.messages.filter(
            is_read=False
        ).exclude(sender=user)
        
        for message in unread_messages:
            message.mark_as_read()
        
        serializer = MessageSerializer(messages, many=True)
        return Response({
            'messages': serializer.data,
            'page': page,
            'page_size': page_size,
            'total_messages': room.messages.count()
        }, status=status.HTTP_200_OK)
    
    @token_required
    def post(self, request, room_id):
        """Отправка сообщения через REST API (альтернатива WebSocket)"""
        user = request.user
        
        try:
            room = ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            return Response(
                {'error': 'Chat room not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Проверяем доступ к комнате
        if user != room.user1 and user != room.user2:
            return Response(
                {'error': 'Access denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        content = request.data.get('content', '').strip()
        if not content:
            return Response(
                {'error': 'Message content is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Создаем сообщение
        message = Message.objects.create(
            chat_room=room,
            sender=user,
            content=content
        )
        
        # Обновляем время последнего обновления комнаты
        room.save()
        
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MarkMessagesReadView(APIView):
    """Отметить сообщения как прочитанные"""
    
    @token_required
    def post(self, request, room_id):
        user = request.user
        
        try:
            room = ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            return Response(
                {'error': 'Chat room not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Проверяем доступ к комнате
        if user != room.user1 and user != room.user2:
            return Response(
                {'error': 'Access denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Отмечаем все непрочитанные сообщения от другого пользователя как прочитанные
        unread_messages = room.messages.filter(
            is_read=False
        ).exclude(sender=user)
        
        updated_count = unread_messages.update(is_read=True)
        
        return Response({
            'marked_read': updated_count
        }, status=status.HTTP_200_OK)

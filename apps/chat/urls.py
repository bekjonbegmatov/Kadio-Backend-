from django.urls import path
from .views import (
    FriendsListView,
    ChatRoomListView,
    ChatRoomDetailView,
    ChatMessagesView,
    MarkMessagesReadView
)

urlpatterns = [
    # Список друзей для чата
    path('friends/', FriendsListView.as_view(), name='chat-friends'),
    
    # Список чат-комнат
    path('rooms/', ChatRoomListView.as_view(), name='chat-rooms'),
    
    # Получение/создание чат-комнаты с другом
    path('rooms/friend/<int:friend_id>/', ChatRoomDetailView.as_view(), name='chat-room-detail'),
    
    # Сообщения в чат-комнате
    path('rooms/<int:room_id>/messages/', ChatMessagesView.as_view(), name='chat-messages'),
    
    # Отметить сообщения как прочитанные
    path('rooms/<int:room_id>/mark-read/', MarkMessagesReadView.as_view(), name='mark-messages-read'),
]
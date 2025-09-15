import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from apps.api_auth.models import UserModel
from .models import ChatRoom, Message
from apps.api.models import Friendship
from django.db.models import Q


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        # Получаем пользователя из токена
        self.user = await self.get_user_from_token()
        
        if self.user is None or isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        # Проверяем, что пользователь имеет доступ к этой комнате
        has_access = await self.check_room_access()
        if not has_access:
            await self.close()
            return
        
        # Присоединяемся к группе комнаты
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Покидаем группу комнаты
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'message')
            
            if message_type == 'message':
                message_content = text_data_json['message']
                
                # Сохраняем сообщение в базу данных
                message = await self.save_message(message_content)
                
                if message:
                    # Отправляем сообщение в группу комнаты
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'message': message_content,
                            'sender_id': self.user.id,
                            'sender_username': self.user.username,
                            'timestamp': message.timestamp.isoformat(),
                            'message_id': message.id
                        }
                    )
            
            elif message_type == 'typing':
                # Обработка индикатора печати
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'typing_indicator',
                        'user_id': self.user.id,
                        'username': self.user.username,
                        'is_typing': text_data_json.get('is_typing', False)
                    }
                )
        
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))
    
    async def chat_message(self, event):
        # Отправляем сообщение в WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id']
        }))
    
    async def typing_indicator(self, event):
        # Не отправляем индикатор печати самому отправителю
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_typing': event['is_typing']
            }))
    
    @database_sync_to_async
    def get_user_from_token(self):
        """Получаем пользователя из токена в query string"""
        try:
            query_string = self.scope.get('query_string', b'').decode()
            token = None
            
            # Парсим query string для получения токена
            for param in query_string.split('&'):
                if param.startswith('token='):
                    token = param.split('=')[1]
                    break
            
            if token:
                user = UserModel.objects.filter(token=token).first()
                return user
            return None
        except Exception:
            return None
    
    @database_sync_to_async
    def check_room_access(self):
        """Проверяем, что пользователь имеет доступ к комнате"""
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            # Проверяем, что пользователь является участником комнаты
            if self.user == room.user1 or self.user == room.user2:
                return True
            return False
        except ChatRoom.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content):
        """Сохраняем сообщение в базу данных"""
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            message = Message.objects.create(
                chat_room=room,
                sender=self.user,
                content=content
            )
            return message
        except Exception:
            return None
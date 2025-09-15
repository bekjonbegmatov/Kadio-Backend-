from django.db import models
from django.utils import timezone
from apps.api_auth.models import UserModel
from apps.api.models import Friendship


class ChatRoom(models.Model):
    """
    Модель для чат-комнаты между двумя друзьями
    """
    user1 = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='chat_rooms_as_user1'
    )
    user2 = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='chat_rooms_as_user2'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user1', 'user2')
        verbose_name = "Chat Room"
        verbose_name_plural = "Chat Rooms"
    
    def __str__(self):
        return f"Chat: {self.user1.username} - {self.user2.username}"
    
    @classmethod
    def get_or_create_room(cls, user1, user2):
        """
        Получить или создать комнату между двумя пользователями
        Проверяет, что пользователи являются друзьями
        """
        # Проверяем, что пользователи друзья
        friendship_exists = Friendship.objects.filter(
            models.Q(
                from_user=user1, to_user=user2, status='accepted'
            ) | models.Q(
                from_user=user2, to_user=user1, status='accepted'
            )
        ).exists()
        
        if not friendship_exists:
            raise ValueError("Users are not friends")
        
        # Упорядочиваем пользователей по ID для консистентности
        if user1.id > user2.id:
            user1, user2 = user2, user1
        
        room, created = cls.objects.get_or_create(
            user1=user1,
            user2=user2
        )
        return room, created
    
    def get_other_user(self, current_user):
        """
        Получить другого пользователя в чате
        """
        if self.user1 == current_user:
            return self.user2
        return self.user1


class Message(models.Model):
    """
    Модель для сообщений в чате
    """
    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
        verbose_name = "Message"
        verbose_name_plural = "Messages"
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}..."
    
    def mark_as_read(self):
        """
        Отметить сообщение как прочитанное
        """
        self.is_read = True
        self.save()

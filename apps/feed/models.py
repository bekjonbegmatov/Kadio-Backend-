from django.db import models
from django.utils import timezone
from apps.api_auth.models import UserModel
import uuid


class Post(models.Model):
    """
    Модель поста в ленте
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    author = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Автор"
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Заголовок"
    )
    content = models.TextField(
        max_length=4000,
        verbose_name="Содержание"
    )
    image = models.ImageField(
        upload_to='post_images/',
        null=True,
        blank=True,
        verbose_name="Изображение"
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Теги"
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name="Опубликован"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    
    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author']),
            models.Index(fields=['is_published']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.author.username}"
    
    @property
    def likes_count(self):
        return self.likes.count()
    
    @property
    def comments_count(self):
        return self.comments.count()
    
    @property
    def views_count(self):
        return self.views.count()


class Comment(models.Model):
    """
    Модель комментария к посту
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Пост"
    )
    author = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Автор"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name="Родительский комментарий"
    )
    content = models.TextField(
        max_length=1000,
        verbose_name="Содержание"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    
    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['author']),
            models.Index(fields=['parent']),
        ]
    
    def __str__(self):
        return f"Комментарий от {self.author.username} к {self.post.title}"


class Like(models.Model):
    """
    Модель лайка поста
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name="Пост"
    )
    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name="Пользователь"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    
    class Meta:
        verbose_name = "Лайк"
        verbose_name_plural = "Лайки"
        unique_together = ['post', 'user']
        indexes = [
            models.Index(fields=['post']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} лайкнул {self.post.title}"


class PostView(models.Model):
    """
    Модель просмотра поста
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='views',
        verbose_name="Пост"
    )
    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='post_views',
        verbose_name="Пользователь",
        null=True,
        blank=True
    )
    ip_address = models.GenericIPAddressField(
        verbose_name="IP адрес",
        null=True,
        blank=True
    )
    user_agent = models.TextField(
        verbose_name="User Agent",
        null=True,
        blank=True
    )
    viewed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата просмотра"
    )
    
    class Meta:
        verbose_name = "Просмотр поста"
        verbose_name_plural = "Просмотры постов"
        indexes = [
            models.Index(fields=['post', 'viewed_at']),
            models.Index(fields=['user']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        user_info = self.user.username if self.user else self.ip_address
        return f"Просмотр {self.post.title} от {user_info}"


class PostRecommendation(models.Model):
    """
    Модель рекомендаций постов для пользователей
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='recommendations',
        verbose_name="Пользователь"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='recommendations',
        verbose_name="Пост"
    )
    score = models.FloatField(
        default=0.0,
        verbose_name="Оценка релевантности"
    )
    reason = models.CharField(
        max_length=255,
        verbose_name="Причина рекомендации",
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    
    class Meta:
        verbose_name = "Рекомендация поста"
        verbose_name_plural = "Рекомендации постов"
        unique_together = ['user', 'post']
        ordering = ['-score', '-created_at']
        indexes = [
            models.Index(fields=['user', '-score']),
            models.Index(fields=['post']),
        ]
    
    def __str__(self):
        return f"Рекомендация {self.post.title} для {self.user.username}"
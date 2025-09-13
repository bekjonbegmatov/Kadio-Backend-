from django.db import models
from django.utils import timezone

from apps.api_auth.models import UserModel


class UserActivity(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    
    def __str__(self) -> str:
        return self.action

class Badge(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='badges/')
    users = models.ManyToManyField(UserModel, related_name='badges', blank=True)

    def add_user(self, user: UserModel) -> None:
        """
        Add a user to the badge's list of users who have earned it
        """
        if user not in self.users.all():
            self.users.add(user)
            self.save()

    def __str__(self) -> str:
        return self.name

class UserNotifications(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='notifications')
    is_read = models.BooleanField(default=False)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    message_from = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='notifications_from')
    
    def __str__(self) -> str:
        return self.message

    def make_read(self) -> None:
        self.is_read = True
        self.save()


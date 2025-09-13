from django.db import models

from apps.api_auth.models import UserModel


class Friendship(models.Model):
    from_user = models.ForeignKey(
        UserModel, related_name="friendship_requests_sent",
        on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        UserModel, related_name="friendship_requests_received",
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Ожидание"),
            ("accepted", "Принято"),
            ("declined", "Отклонено"),
        ],
        default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("from_user", "to_user")  

    def __str__(self):
        return f"{self.from_user} -> {self.to_user} ({self.status})"
    

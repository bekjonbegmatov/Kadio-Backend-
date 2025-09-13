from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import uuid
class UserModel(models.Model):
    """
    Custom user model for authentication and user data storage
    """
    # Required fields for authentication
    email = models.EmailField(
        max_length=255,
        unique=True,
        null=False,
        blank=False,
        verbose_name="Email address"
    )
    password = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        verbose_name="Password"
    )
    username = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Username"
    )

    # User progress fields
    streak_days = models.IntegerField(
        default=0,
        verbose_name="Streak days"
    )
    level = models.IntegerField(
        default=0,
        verbose_name="User level"
    )
    interests = models.JSONField(
        blank=True,
        default=dict,
        verbose_name="User interests"
    )

    # Profile fields
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name="Profile picture"
    )
    full_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Full name"
    )
    link = models.URLField(
        null=True,
        blank=True,
        verbose_name="User link"
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date of birth"
    )
    bio = models.TextField(
        null=True,
        blank=True,
        verbose_name="User biography"
    )
    user_time_zone = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="User timezone"
    )
    last_active = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Last active timestamp"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active status"
    )

    # Balance
    diamonds = models.IntegerField(
        default=0,
        verbose_name="Diamonds balance"
    )
    coins = models.IntegerField(
        default=0,
        verbose_name="Coins balance"
    )

    # Authentication token
    token = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Authentication token"
    )

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created timestamp"
    )
    updated = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated timestamp"
    )
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-id']

    def __str__(self):
        return self.email

    def generate_token(self):
        """Generate unique token for user authentication"""
        self.token = str(uuid.uuid4())
        self.save()
        return self.token

    def set_password(self, raw_password):
        """Hash password before saving"""
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        """Verify if provided password matches stored hash"""
        return check_password(raw_password, self.password)



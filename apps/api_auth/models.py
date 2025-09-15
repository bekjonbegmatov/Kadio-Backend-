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
    
    def get_purchased_courses(self):
        """Получить все купленные курсы пользователя"""
        from apps.cours.models import UserCourseModel
        return UserCourseModel.objects.filter(
            user=self, 
            is_purchased=True
        ).select_related('course')
    
    def get_available_courses(self):
        """Получить все доступные курсы для пользователя по уровню"""
        from apps.cours.models import CourseModel
        return CourseModel.objects.filter(min_level__lte=self.level)
    
    def get_completed_courses(self):
        """Получить все завершенные курсы пользователя"""
        from apps.cours.models import UserCourseModel
        return UserCourseModel.objects.filter(
            user=self, 
            is_completed=True
        ).select_related('course')
    
    def can_purchase_course(self, course):
        """Проверить, может ли пользователь купить курс"""
        # Проверяем уровень
        if self.level < course.min_level:
            return False, "Недостаточный уровень"
        
        # Проверяем, не куплен ли уже курс
        from apps.cours.models import UserCourseModel
        if UserCourseModel.objects.filter(user=self, course=course, is_purchased=True).exists():
            return False, "Курс уже куплен"
        
        # Проверяем баланс (используем coins как основную валюту для курсов)
        if self.coins < course.price:
            return False, "Недостаточно монет"
        
        return True, "Можно купить"
    
    def purchase_course(self, course):
        """Купить курс"""
        can_purchase, message = self.can_purchase_course(course)
        if not can_purchase:
            return False, message
        
        # Списываем монеты
        self.coins -= course.price
        self.save()
        
        # Создаем запись о покупке курса
        from apps.cours.models import UserCourseModel
        user_course, created = UserCourseModel.objects.get_or_create(
            user=self,
            course=course,
            defaults={'is_purchased': True}
        )
        
        if not created:
            user_course.is_purchased = True
            user_course.save()
        
        return True, "Курс успешно куплен"



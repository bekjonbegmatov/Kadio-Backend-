from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import serializers
from .models import (
    CourseModel, 
    CourseLessonModel, 
    UserCourseModel, 
    CourseCommentModel, 
    LessonCommentModel
)
from apps.api_auth.models import UserModel


class UserBasicSerializer(ModelSerializer):
    """Базовый сериализатор пользователя для отображения в курсах"""
    class Meta:
        model = UserModel
        fields = ['id', 'username', 'full_name', 'avatar', 'level']


class CourseLessonSerializer(ModelSerializer):
    """Сериализатор для уроков курса"""
    comments_count = SerializerMethodField()
    
    class Meta:
        model = CourseLessonModel
        fields = [
            'id', 'name', 'description', 'video', 'order', 
            'reward_points', 'created_at', 'updated_at', 'comments_count'
        ]
    
    def get_comments_count(self, obj):
        return obj.comments.count()


class CourseSerializer(ModelSerializer):
    """Сериализатор для курсов"""
    lessons = CourseLessonSerializer(many=True, read_only=True)
    comments_count = SerializerMethodField()
    average_rating = SerializerMethodField()
    is_purchased = SerializerMethodField()
    is_available = SerializerMethodField()
    progress = SerializerMethodField()
    
    class Meta:
        model = CourseModel
        fields = [
            'id', 'name', 'description', 'price', 'min_level', 'preview',
            'lessons_count', 'total_reward_points', 'created_at', 'updated_at',
            'lessons', 'comments_count', 'average_rating', 'is_purchased', 
            'is_available', 'progress'
        ]
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    
    def get_average_rating(self, obj):
        comments = obj.comments.all()
        if comments:
            return sum(comment.rating for comment in comments) / len(comments)
        return 0
    
    def get_is_purchased(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and isinstance(request.user, UserModel):
            return UserCourseModel.objects.filter(
                user=request.user, 
                course=obj, 
                is_purchased=True
            ).exists()
        return False
    
    def get_is_available(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and isinstance(request.user, UserModel):
            return request.user.level >= obj.min_level
        return True  # Курсы доступны для просмотра всем
    
    def get_progress(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and isinstance(request.user, UserModel):
            try:
                user_course = UserCourseModel.objects.get(
                    user=request.user, 
                    course=obj
                )
                total_lessons = obj.lessons.count()
                completed_lessons = user_course.completed_lessons.count()
                if total_lessons > 0:
                    return {
                        'completed_lessons': completed_lessons,
                        'total_lessons': total_lessons,
                        'percentage': (completed_lessons / total_lessons) * 100,
                        'earned_points': user_course.earned_points,
                        'is_completed': user_course.is_completed
                    }
            except UserCourseModel.DoesNotExist:
                pass
        return {
            'completed_lessons': 0,
            'total_lessons': obj.lessons.count(),
            'percentage': 0,
            'earned_points': 0,
            'is_completed': False
        }


class CourseListSerializer(ModelSerializer):
    """Упрощенный сериализатор для списка курсов"""
    comments_count = SerializerMethodField()
    average_rating = SerializerMethodField()
    is_purchased = SerializerMethodField()
    is_available = SerializerMethodField()
    
    class Meta:
        model = CourseModel
        fields = [
            'id', 'name', 'description', 'price', 'min_level', 'preview',
            'lessons_count', 'total_reward_points', 'created_at',
            'comments_count', 'average_rating', 'is_purchased', 'is_available'
        ]
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    
    def get_average_rating(self, obj):
        comments = obj.comments.all()
        if comments:
            return sum(comment.rating for comment in comments) / len(comments)
        return 0
    
    def get_is_purchased(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and isinstance(request.user, UserModel):
            return UserCourseModel.objects.filter(
                user=request.user, 
                course=obj, 
                is_purchased=True
            ).exists()
        return False
    
    def get_is_available(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and isinstance(request.user, UserModel):
            return request.user.level >= obj.min_level
        return True  # Курсы доступны для просмотра всем


class UserCourseSerializer(ModelSerializer):
    """Сериализатор для курсов пользователя"""
    course = CourseListSerializer(read_only=True)
    completed_lessons_count = SerializerMethodField()
    progress_percentage = SerializerMethodField()
    
    class Meta:
        model = UserCourseModel
        fields = [
            'id', 'course', 'earned_points', 'is_purchased', 'is_completed',
            'purchase_date', 'completion_date', 'completed_lessons_count',
            'progress_percentage'
        ]
    
    def get_completed_lessons_count(self, obj):
        return obj.completed_lessons.count()
    
    def get_progress_percentage(self, obj):
        total_lessons = obj.course.lessons.count()
        completed_lessons = obj.completed_lessons.count()
        if total_lessons > 0:
            return (completed_lessons / total_lessons) * 100
        return 0


class CourseCommentSerializer(ModelSerializer):
    """Сериализатор для комментариев к курсам"""
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = CourseCommentModel
        fields = [
            'id', 'user', 'text', 'rating', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user']


class LessonCommentSerializer(ModelSerializer):
    """Сериализатор для комментариев к урокам"""
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = LessonCommentModel
        fields = [
            'id', 'user', 'text', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user']


class CoursePurchaseSerializer(serializers.Serializer):
    """Сериализатор для покупки курса"""
    course_id = serializers.IntegerField()
    
    def validate_course_id(self, value):
        try:
            course = CourseModel.objects.get(id=value)
            return value
        except CourseModel.DoesNotExist:
            raise serializers.ValidationError("Курс не найден")


class LessonCompleteSerializer(serializers.Serializer):
    """Сериализатор для завершения урока"""
    lesson_id = serializers.IntegerField()
    
    def validate_lesson_id(self, value):
        try:
            lesson = CourseLessonModel.objects.get(id=value)
            return value
        except CourseLessonModel.DoesNotExist:
            raise serializers.ValidationError("Урок не найден")
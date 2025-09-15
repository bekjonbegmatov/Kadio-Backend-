from django.db import models
from apps.api_auth.models import UserModel

class CourseModel(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.PositiveIntegerField(default=0, help_text="Course price in points")
    min_level = models.PositiveIntegerField(default=0)
    preview = models.ImageField(upload_to='course_photos/', blank=True, null=True)
    lessons_count = models.PositiveIntegerField(default=0)
    total_reward_points = models.PositiveIntegerField(default=0, help_text="Total points user gets after completing course")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        
class CourseLessonModel(models.Model):
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE, related_name='lessons')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    video = models.FileField(upload_to='course_videos/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="Lesson order in course")
    reward_points = models.PositiveIntegerField(default=0, help_text="Points awarded for completing this lesson")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Course Lesson'
        verbose_name_plural = 'Course Lessons'
        ordering = ['order']
        
class UserCourseModel(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='enrolled_courses')
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE, related_name='enrolled_users')
    completed_lessons = models.ManyToManyField(CourseLessonModel, related_name='completed_by_users', blank=True)
    earned_points = models.PositiveIntegerField(default=0, help_text="Points earned from completed lessons")
    
    is_purchased = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    purchase_date = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'course']
    
class CourseCommentModel(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='course_comments')
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    rating = models.PositiveIntegerField(default=0, choices=[(i, i) for i in range(1, 6)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.text[:20]
    
    class Meta:
        verbose_name = 'Course Comment'
        verbose_name_plural = 'Course Comments'
    
class LessonCommentModel(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='lesson_comments')
    lesson = models.ForeignKey(CourseLessonModel, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.text[:20]
    
    class Meta:
        verbose_name = 'Lesson Comment'
        verbose_name_plural = 'Lesson Comments'

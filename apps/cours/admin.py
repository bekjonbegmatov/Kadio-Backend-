from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from django.forms import Textarea
from .models import (
    CourseModel,
    CourseLessonModel,
    UserCourseModel,
    CourseCommentModel,
    LessonCommentModel
)


class CourseLessonInline(admin.TabularInline):
    """Inline для уроков курса"""
    model = CourseLessonModel
    extra = 1
    fields = ('name', 'order', 'reward_points')
    ordering = ('order',)


@admin.register(CourseModel)
class CourseAdmin(admin.ModelAdmin):
    """Админка для курсов с поддержкой markdown"""
    
    list_display = (
        'name', 
        'price', 
        'min_level', 
        'lessons_count',
        'total_reward_points',
        'created_at'
    )
    
    list_filter = (
        'min_level',
        'created_at',
        'updated_at'
    )
    
    search_fields = ('name', 'description')
    
    readonly_fields = (
        'created_at', 
        'updated_at', 
        'lessons_count', 
        'total_reward_points'
    )
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'name',
                'description',
                'preview'
            )
        }),
        ('Цена и требования', {
            'fields': (
                'price', 
                'min_level'
            )
        }),
        ('Статистика (только для чтения)', {
            'fields': (
                'lessons_count',
                'total_reward_points',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    inlines = [CourseLessonInline]
    
    # Настройка виджетов для markdown полей
    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(attrs={
                'rows': 10,
                'cols': 80,
                'placeholder': 'Используйте Markdown для форматирования текста\n\n# Заголовок\n## Подзаголовок\n**Жирный текст**\n*Курсив*\n- Список\n1. Нумерованный список\n\n```python\n# Код\nprint("Hello World")\n```'
            })
        }
    }
    
    def lessons_count(self, obj):
        """Количество уроков в курсе"""
        return obj.lessons.count()
    lessons_count.short_description = 'Количество уроков'
    
    def total_duration_display(self, obj):
        """Общая продолжительность курса"""
        total_minutes = obj.total_duration
        hours = total_minutes // 60
        minutes = total_minutes % 60
        if hours > 0:
            return f"{hours}ч {minutes}м"
        return f"{minutes}м"
    total_duration_display.short_description = 'Общая продолжительность'
    
    def get_queryset(self, request):
        """Оптимизация запросов"""
        return super().get_queryset(request).prefetch_related('lessons')


@admin.register(CourseLessonModel)
class CourseLessonAdmin(admin.ModelAdmin):
    """Админка для уроков с поддержкой markdown"""
    
    list_display = (
        'name',
        'course',
        'order',
        'reward_points',
        'created_at'
    )
    
    list_filter = (
        'course',
        'created_at'
    )
    
    search_fields = ('name', 'description', 'course__name')
    
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'course',
                'name',
                'description',
                'order'
            )
        }),
        ('Параметры урока', {
            'fields': (
                'reward_points',
                'video'
            )
        }),
        ('Метаданные', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    # Настройка виджетов для markdown полей
    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(attrs={
                'rows': 15,
                'cols': 80,
                'placeholder': 'Используйте Markdown для форматирования содержимого урока\n\n# Заголовок урока\n\n## Теория\nОписание теоретической части...\n\n## Практика\n1. Шаг 1\n2. Шаг 2\n\n```python\n# Пример кода\ndef example():\n    pass\n```\n\n## Задания\n- [ ] Задание 1\n- [ ] Задание 2'
            })
        }
    }
    
    def get_queryset(self, request):
        """Оптимизация запросов"""
        return super().get_queryset(request).select_related('course')


@admin.register(UserCourseModel)
class UserCourseAdmin(admin.ModelAdmin):
    """Админка для записей пользователей на курсы"""
    
    list_display = (
        'user',
        'course',
        'is_purchased',
        'is_completed',
        'earned_points',
        'progress_percentage',
        'created_at'
    )
    
    list_filter = (
        'is_purchased',
        'is_completed',
        'created_at',
        'completion_date'
    )
    
    search_fields = (
        'user__username',
        'user__email',
        'course__name'
    )
    
    readonly_fields = (
        'created_at',
        'updated_at',
        'progress_percentage',
        'completed_lessons_display'
    )
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'user',
                'course',
                'is_purchased',
                'is_completed'
            )
        }),
        ('Прогресс', {
            'fields': (
                'earned_points',
                'progress_percentage',
                'completed_lessons_display',
                'completion_date'
            )
        }),
        ('Метаданные', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    def progress_percentage(self, obj):
        """Процент прогресса"""
        total_lessons = obj.course.lessons.count()
        if total_lessons == 0:
            return "0%"
        completed = obj.completed_lessons.count()
        percentage = (completed / total_lessons) * 100
        return f"{percentage:.1f}%"
    progress_percentage.short_description = 'Прогресс'
    
    def completed_lessons_display(self, obj):
        """Отображение завершенных уроков"""
        completed = obj.completed_lessons.count()
        total = obj.course.lessons.count()
        return f"{completed} из {total}"
    completed_lessons_display.short_description = 'Завершенные уроки'
    
    def get_queryset(self, request):
        """Оптимизация запросов"""
        return super().get_queryset(request).select_related(
            'user', 'course'
        ).prefetch_related('completed_lessons')


@admin.register(CourseCommentModel)
class CourseCommentAdmin(admin.ModelAdmin):
    """Админка для комментариев к курсам"""
    
    list_display = (
        'user',
        'course',
        'content_preview',
        'created_at'
    )
    
    list_filter = (
        'created_at',
        'course'
    )
    
    search_fields = (
        'user__username',
        'course__name',
        'content'
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def content_preview(self, obj):
        """Превью содержимого комментария"""
        if len(obj.content) > 50:
            return obj.content[:50] + '...'
        return obj.content
    content_preview.short_description = 'Содержимое'
    
    def get_queryset(self, request):
        """Оптимизация запросов"""
        return super().get_queryset(request).select_related('user', 'course')


@admin.register(LessonCommentModel)
class LessonCommentAdmin(admin.ModelAdmin):
    """Админка для комментариев к урокам"""
    
    list_display = (
        'user',
        'lesson',
        'lesson_course',
        'content_preview',
        'created_at'
    )
    
    list_filter = (
        'created_at',
        'lesson__course'
    )
    
    search_fields = (
        'user__username',
        'lesson__name',
        'lesson__course__name',
        'content'
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def lesson_course(self, obj):
        """Курс урока"""
        return obj.lesson.course.name
    lesson_course.short_description = 'Курс'
    
    def content_preview(self, obj):
        """Превью содержимого комментария"""
        if len(obj.content) > 50:
            return obj.content[:50] + '...'
        return obj.content
    content_preview.short_description = 'Содержимое'
    
    def get_queryset(self, request):
        """Оптимизация запросов"""
        return super().get_queryset(request).select_related(
            'user', 'lesson', 'lesson__course'
        )


# Настройка заголовков админки
admin.site.site_header = "Kadio - Управление курсами"
admin.site.site_title = "Kadio Admin"
admin.site.index_title = "Добро пожаловать в панель управления курсами"

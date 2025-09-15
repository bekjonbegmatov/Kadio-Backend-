from django.contrib import admin
from .models import Post, Comment, Like, PostView, PostRecommendation


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'is_published', 'likes_count', 'comments_count', 'views_count', 'created_at']
    list_filter = ['is_published', 'created_at', 'author']
    search_fields = ['title', 'content', 'author__username', 'author__email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'likes_count', 'comments_count', 'views_count']
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('id', 'title', 'author', 'content', 'image')
        }),
        ('Метаданные', {
            'fields': ('tags', 'is_published')
        }),
        ('Статистика', {
            'fields': ('likes_count', 'comments_count', 'views_count'),
            'classes': ('collapse',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'parent', 'content_preview', 'created_at']
    list_filter = ['created_at', 'post', 'author']
    search_fields = ['content', 'author__username', 'post__title']
    readonly_fields = ['id', 'created_at', 'updated_at']
    list_per_page = 50
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Превью содержания'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'created_at']
    list_filter = ['created_at', 'post', 'user']
    search_fields = ['post__title', 'user__username']
    readonly_fields = ['id', 'created_at']
    list_per_page = 100
    date_hierarchy = 'created_at'


@admin.register(PostView)
class PostViewAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'ip_address', 'viewed_at']
    list_filter = ['viewed_at', 'post', 'user']
    search_fields = ['post__title', 'user__username', 'ip_address']
    readonly_fields = ['id', 'viewed_at']
    list_per_page = 100
    date_hierarchy = 'viewed_at'


@admin.register(PostRecommendation)
class PostRecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'score', 'reason', 'created_at']
    list_filter = ['created_at', 'score', 'user']
    search_fields = ['user__username', 'post__title', 'reason']
    readonly_fields = ['id', 'created_at']
    list_per_page = 50
    date_hierarchy = 'created_at'
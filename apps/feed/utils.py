from django.db.models import Count, Q, F
from django.utils import timezone
from datetime import timedelta
from .models import Post, Like, PostView, Comment
from apps.api_auth.models import UserModel
import random


class RecommendationEngine:
    """
    Рекомендательная система для постов
    
    Алгоритм работы:
    1. Контентная фильтрация - рекомендует посты на основе тегов постов, которые лайкал пользователь
    2. Коллаборативная фильтрация - рекомендует посты на основе активности похожих пользователей
    3. Популярные посты - рекомендует популярные посты за последнее время
    4. Новые посты - добавляет новые посты для разнообразия
    
    Финальный рейтинг формируется как взвешенная сумма всех факторов.
    """
    
    def __init__(self):
        self.content_weight = 0.4  # Вес контентной фильтрации
        self.collaborative_weight = 0.3  # Вес коллаборативной фильтрации
        self.popularity_weight = 0.2  # Вес популярности
        self.freshness_weight = 0.1  # Вес новизны
    
    def get_recommendations_for_user(self, user, limit=20):
        """
        Получить рекомендации для пользователя
        """
        # Получаем все посты, исключая посты самого пользователя
        base_queryset = Post.objects.filter(
            is_published=True
        ).exclude(
            author=user
        ).select_related('author').annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments'),
            views_count=Count('views')
        )
        
        # Исключаем посты, которые пользователь уже просматривал
        viewed_posts = PostView.objects.filter(user=user).values_list('post_id', flat=True)
        base_queryset = base_queryset.exclude(id__in=viewed_posts)
        
        recommendations = []
        
        # 1. Контентная фильтрация
        content_recommendations = self._get_content_based_recommendations(user, base_queryset)
        recommendations.extend(content_recommendations)
        
        # 2. Коллаборативная фильтрация
        collaborative_recommendations = self._get_collaborative_recommendations(user, base_queryset)
        recommendations.extend(collaborative_recommendations)
        
        # 3. Популярные посты
        popular_recommendations = self._get_popular_recommendations(base_queryset)
        recommendations.extend(popular_recommendations)
        
        # 4. Новые посты
        fresh_recommendations = self._get_fresh_recommendations(base_queryset)
        recommendations.extend(fresh_recommendations)
        
        # Убираем дубликаты и сортируем по рейтингу
        unique_recommendations = {}
        for post, score, reason in recommendations:
            if post.id not in unique_recommendations:
                unique_recommendations[post.id] = (post, score, reason)
            else:
                # Суммируем рейтинги для одинаковых постов
                existing_post, existing_score, existing_reason = unique_recommendations[post.id]
                new_score = existing_score + score
                new_reason = f"{existing_reason}, {reason}"
                unique_recommendations[post.id] = (existing_post, new_score, new_reason)
        
        # Сортируем по рейтингу и возвращаем топ постов
        sorted_recommendations = sorted(
            unique_recommendations.values(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [post for post, score, reason in sorted_recommendations[:limit]]
    
    def _get_content_based_recommendations(self, user, queryset):
        """
        Контентная фильтрация на основе тегов лайкнутых постов
        """
        # Получаем теги постов, которые лайкал пользователь
        liked_posts = Like.objects.filter(user=user).values_list('post', flat=True)
        user_tags = []
        
        for post in Post.objects.filter(id__in=liked_posts):
            if post.tags:
                user_tags.extend(post.tags)
        
        if not user_tags:
            return []
        
        # Подсчитываем частоту тегов
        tag_counts = {}
        for tag in user_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        recommendations = []
        
        # Ищем посты с похожими тегами
        for post in queryset:
            if not post.tags:
                continue
            
            score = 0
            for tag in post.tags:
                if tag in tag_counts:
                    score += tag_counts[tag] * self.content_weight
            
            if score > 0:
                recommendations.append((post, score, "похожие интересы"))
        
        return recommendations
    
    def _get_collaborative_recommendations(self, user, queryset):
        """
        Коллаборативная фильтрация на основе похожих пользователей
        """
        # Находим пользователей с похожими интересами
        user_likes = set(Like.objects.filter(user=user).values_list('post_id', flat=True))
        
        if not user_likes:
            return []
        
        similar_users = []
        
        # Ищем пользователей, которые лайкали те же посты
        for other_user in UserModel.objects.exclude(id=user.id):
            other_likes = set(Like.objects.filter(user=other_user).values_list('post_id', flat=True))
            
            if not other_likes:
                continue
            
            # Вычисляем коэффициент Жаккара (пересечение / объединение)
            intersection = len(user_likes.intersection(other_likes))
            union = len(user_likes.union(other_likes))
            
            if union > 0 and intersection >= 2:  # Минимум 2 общих лайка
                similarity = intersection / union
                similar_users.append((other_user, similarity))
        
        # Сортируем по схожести
        similar_users.sort(key=lambda x: x[1], reverse=True)
        
        recommendations = []
        
        # Рекомендуем посты от похожих пользователей
        for similar_user, similarity in similar_users[:10]:  # Топ 10 похожих пользователей
            similar_user_likes = Like.objects.filter(user=similar_user).values_list('post_id', flat=True)
            
            for post in queryset.filter(id__in=similar_user_likes):
                score = similarity * self.collaborative_weight
                recommendations.append((post, score, "похожие пользователи"))
        
        return recommendations
    
    def _get_popular_recommendations(self, queryset):
        """
        Рекомендации на основе популярности за последнюю неделю
        """
        week_ago = timezone.now() - timedelta(days=7)
        
        popular_posts = queryset.filter(
            created_at__gte=week_ago
        ).annotate(
            popularity_score=(
                F('likes_count') * 3 +  # Лайки весят больше
                F('comments_count') * 2 +  # Комментарии тоже важны
                F('views_count')  # Просмотры учитываются
            )
        ).filter(
            popularity_score__gt=0
        ).order_by('-popularity_score')[:20]
        
        recommendations = []
        for post in popular_posts:
            score = (post.popularity_score or 0) * self.popularity_weight
            recommendations.append((post, score, "популярное"))
        
        return recommendations
    
    def _get_fresh_recommendations(self, queryset):
        """
        Рекомендации новых постов для разнообразия
        """
        day_ago = timezone.now() - timedelta(days=1)
        
        fresh_posts = queryset.filter(
            created_at__gte=day_ago
        ).order_by('-created_at')[:10]
        
        recommendations = []
        for post in fresh_posts:
            # Новые посты получают базовый рейтинг
            score = self.freshness_weight
            recommendations.append((post, score, "новое"))
        
        return recommendations
    
    def get_trending_tags(self, days=7):
        """
        Получить популярные теги за последние дни
        """
        since_date = timezone.now() - timedelta(days=days)
        
        posts = Post.objects.filter(
            created_at__gte=since_date,
            is_published=True
        ).exclude(tags__isnull=True)
        
        tag_counts = {}
        for post in posts:
            if post.tags:
                for tag in post.tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Сортируем по популярности
        trending_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        return trending_tags[:20]  # Топ 20 тегов
    
    def get_similar_posts(self, post, limit=5):
        """
        Получить похожие посты на основе тегов
        """
        if not post.tags:
            return Post.objects.none()
        
        similar_posts = Post.objects.filter(
            is_published=True
        ).exclude(
            id=post.id
        ).select_related('author').annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments'),
            views_count=Count('views')
        )
        
        # Ищем посты с пересекающимися тегами
        scored_posts = []
        for similar_post in similar_posts:
            if not similar_post.tags:
                continue
            
            # Подсчитываем количество общих тегов
            common_tags = set(post.tags).intersection(set(similar_post.tags))
            if common_tags:
                score = len(common_tags)
                scored_posts.append((similar_post, score))
        
        # Сортируем по количеству общих тегов
        scored_posts.sort(key=lambda x: x[1], reverse=True)
        
        return [post for post, score in scored_posts[:limit]]
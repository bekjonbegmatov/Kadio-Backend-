from functools import wraps
from django.http import JsonResponse
from django.utils import timezone
from .models import UserModel


def token_required(view_func):
    """
    Декоратор для проверки токена аутентификации.
    Применяется только к тем view функциям, где нужна аутентификация.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Получаем токен из заголовка Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header:
            return JsonResponse(
                {'error': 'Authentication required. Token not provided.'},
                status=401
            )
        
        # Проверяем формат токена
        if not auth_header.startswith('Token '):
            return JsonResponse(
                {'error': 'Invalid token format. Use "Token <your_token>".'},
                status=401
            )
        
        # Извлекаем токен
        token = auth_header.split(' ')[1]
        
        # Ищем пользователя по токену
        try:
            user = UserModel.objects.get(token=token)
            user.last_active = timezone.now()
            user.save()
            
            # Добавляем пользователя в request
            request.user = user
            request._authenticated_user = user
            
            return view_func(request, *args, **kwargs)
            
        except UserModel.DoesNotExist:
            return JsonResponse(
                {'error': 'Access denied. Invalid token.'},
                status=401
            )
    
    return wrapper
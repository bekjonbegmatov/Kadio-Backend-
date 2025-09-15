# Django imports
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Rest Framework imports
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

# Local imports
from .models import UserModel
from .serializers import UserAuthSerializer, UserSerializer
from .decorators import token_required


@csrf_exempt
@api_view(['POST'])
def register_user(request):
    """
    Register a new user
    """
    serializer = UserAuthSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )
    return Response(
        data=serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )

@csrf_exempt
@api_view(['POST'])
def login_user(request):
    """
    Login user
    """
    email = request.data.get('email')
    password = request.data.get('password')
    user = UserModel.objects.filter(email=email).first()
    if user is None:
        return Response(
            data={'error': 'User or password is not correct'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if not user.check_password(password):
        return Response(
            data={'error': 'User or password is not correct'},
            status=status.HTTP_400_BAD_REQUEST
        )
    user.generate_token()
    return Response(
        data={
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'token': user.token
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
def get_all_users(request):
    """
    Get list of all users
    """
    users = UserModel.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(data=serializer.data)


@api_view(['GET'])
@token_required
def get_user_profile(request):
    """
    Получить профиль текущего пользователя
    """
    # Декоратор уже проверил аутентификацию и установил request.user
    user = request.user
    serializer = UserSerializer(user, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['PUT'])
@token_required
def update_user_profile(request):
    """
    Обновление профиля пользователя
    """
    # Декоратор уже проверил аутентификацию и установил request.user
    user = request.user
    
    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
@token_required
def upload_avatar(request):
    """
    Загрузить аватарку для текущего пользователя
    """
    # Декоратор уже проверил аутентификацию и установил request.user
    user = request.user
    
    if 'avatar' not in request.FILES:
        return Response(
            {'error': 'Файл аватарки не найден'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    avatar_file = request.FILES['avatar']
    
    # Проверка типа файла
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
    if avatar_file.content_type not in allowed_types:
        return Response(
            {'error': 'Неподдерживаемый тип файла. Разрешены: JPEG, PNG, GIF'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Проверка размера файла (максимум 5MB)
    if avatar_file.size > 5 * 1024 * 1024:
        return Response(
            {'error': 'Размер файла слишком большой. Максимум 5MB'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Сохранение аватарки
    user.avatar = avatar_file
    user.save()
    
    return Response(
        {
            'message': 'Аватарка успешно загружена',
            'avatar_url': request.build_absolute_uri(user.avatar.url) if user.avatar else None
        }, 
        status=status.HTTP_200_OK
    )
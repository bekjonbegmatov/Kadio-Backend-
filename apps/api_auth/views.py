# Django imports
from django.shortcuts import render

# Rest Framework imports
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

# Local imports
from .models import UserModel
from .serializers import UserAuthSerializer, UserSerializer


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
def get_user_profile(request):
    """
    Получить профиль текущего пользователя.
    Этот эндпоинт защищен middleware и требует токен аутентификации.
    """
    # Объект пользователя доступен через request.user благодаря middleware
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)
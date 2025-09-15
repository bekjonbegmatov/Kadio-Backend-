from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from apps.api_auth.decorators import token_required
from .models import (
    CourseModel, 
    CourseLessonModel, 
    UserCourseModel, 
    CourseCommentModel, 
    LessonCommentModel
)
from .serializers import (
    CourseSerializer,
    CourseListSerializer,
    CourseLessonSerializer,
    UserCourseSerializer,
    CourseCommentSerializer,
    LessonCommentSerializer,
    CoursePurchaseSerializer,
    LessonCompleteSerializer
)


class CourseListView(APIView):
    """Получение списка всех курсов (публичный endpoint)"""
    
    def get(self, request):
        courses = CourseModel.objects.all().order_by('-created_at')
        serializer = CourseListSerializer(courses, many=True, context={'request': request})
        return Response({
            'success': True,
            'data': serializer.data,
            'count': courses.count()
        })


class CourseDetailView(APIView):
    """Получение детальной информации о курсе (публичный endpoint)"""
    
    def get(self, request, course_id):
        try:
            course = CourseModel.objects.get(id=course_id)
            serializer = CourseSerializer(course, context={'request': request})
            return Response({
                'success': True,
                'data': serializer.data
            })
        except CourseModel.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Курс не найден'
            }, status=status.HTTP_404_NOT_FOUND)


class CourseLessonsView(APIView):
    """Получение уроков курса (публичный endpoint)"""
    
    def get(self, request, course_id):
        try:
            course = CourseModel.objects.get(id=course_id)
            lessons = course.lessons.all().order_by('order')
            serializer = CourseLessonSerializer(lessons, many=True)
            return Response({
                'success': True,
                'data': serializer.data,
                'count': lessons.count()
            })
        except CourseModel.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Курс не найден'
            }, status=status.HTTP_404_NOT_FOUND)


class CourseCommentsView(APIView):
    """Получение и создание комментариев к курсу"""
    
    def get(self, request, course_id):
        """Получение комментариев к курсу (публичный endpoint)"""
        try:
            course = CourseModel.objects.get(id=course_id)
            comments = course.comments.all().order_by('-created_at')
            serializer = CourseCommentSerializer(comments, many=True)
            return Response({
                'success': True,
                'data': serializer.data,
                'count': comments.count()
            })
        except CourseModel.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Курс не найден'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @token_required
    def post(self, request, course_id):
        """Создание комментария к курсу (требует авторизации)"""
        try:
            course = CourseModel.objects.get(id=course_id)
            serializer = CourseCommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user, course=course)
                return Response({
                    'success': True,
                    'data': serializer.data,
                    'message': 'Комментарий успешно добавлен'
                }, status=status.HTTP_201_CREATED)
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except CourseModel.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Курс не найден'
            }, status=status.HTTP_404_NOT_FOUND)


class LessonCommentsView(APIView):
    """Получение и создание комментариев к уроку"""
    
    def get(self, request, lesson_id):
        """Получение комментариев к уроку (публичный endpoint)"""
        try:
            lesson = CourseLessonModel.objects.get(id=lesson_id)
            comments = lesson.comments.all().order_by('-created_at')
            serializer = LessonCommentSerializer(comments, many=True)
            return Response({
                'success': True,
                'data': serializer.data,
                'count': comments.count()
            })
        except CourseLessonModel.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Урок не найден'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @token_required
    def post(self, request, lesson_id):
        """Создание комментария к уроку (требует авторизации)"""
        try:
            lesson = CourseLessonModel.objects.get(id=lesson_id)
            serializer = LessonCommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user, lesson=lesson)
                return Response({
                    'success': True,
                    'data': serializer.data,
                    'message': 'Комментарий успешно добавлен'
                }, status=status.HTTP_201_CREATED)
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except CourseLessonModel.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Урок не найден'
            }, status=status.HTTP_404_NOT_FOUND)


class UserCoursesView(APIView):
    """Получение купленных курсов пользователя (требует авторизации)"""
    
    @token_required
    def get(self, request):
        # Получаем только купленные курсы
        user_courses = request.user.enrolled_courses.filter(is_purchased=True).order_by('-created_at')
        serializer = UserCourseSerializer(user_courses, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'count': user_courses.count()
        })


class CoursePurchaseView(APIView):
    """Покупка курса (требует авторизации)"""
    
    @token_required
    def post(self, request):
        serializer = CoursePurchaseSerializer(data=request.data)
        if serializer.is_valid():
            course_id = serializer.validated_data['course_id']
            try:
                course = CourseModel.objects.get(id=course_id)
                success, message = request.user.purchase_course(course)
                
                if success:
                    return Response({
                        'success': True,
                        'message': message,
                        'user_balance': {
                            'coins': request.user.coins,
                            'diamonds': request.user.diamonds
                        }
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        'success': False,
                        'error': message
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except CourseModel.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Курс не найден'
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LessonCompleteView(APIView):
    """Завершение урока (требует авторизации)"""
    
    @token_required
    def post(self, request):
        serializer = LessonCompleteSerializer(data=request.data)
        if serializer.is_valid():
            lesson_id = serializer.validated_data['lesson_id']
            try:
                lesson = CourseLessonModel.objects.get(id=lesson_id)
                
                # Проверяем, купил ли пользователь курс
                try:
                    user_course = UserCourseModel.objects.get(
                        user=request.user,
                        course=lesson.course,
                        is_purchased=True
                    )
                except UserCourseModel.DoesNotExist:
                    return Response({
                        'success': False,
                        'error': 'Курс не куплен'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # Проверяем, не завершен ли уже урок
                if user_course.completed_lessons.filter(id=lesson.id).exists():
                    return Response({
                        'success': False,
                        'error': 'Урок уже завершен'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Завершаем урок
                user_course.completed_lessons.add(lesson)
                user_course.earned_points += lesson.reward_points
                
                # Добавляем баллы пользователю
                request.user.coins += lesson.reward_points
                request.user.save()
                
                # Проверяем, завершен ли весь курс
                total_lessons = lesson.course.lessons.count()
                completed_lessons = user_course.completed_lessons.count()
                
                if completed_lessons == total_lessons and not user_course.is_completed:
                    user_course.is_completed = True
                    user_course.completion_date = timezone.now()
                    
                    # Добавляем бонусные баллы за завершение курса
                    bonus_points = lesson.course.total_reward_points
                    user_course.earned_points += bonus_points
                    request.user.coins += bonus_points
                    request.user.save()
                
                user_course.save()
                
                return Response({
                    'success': True,
                    'message': 'Урок успешно завершен',
                    'earned_points': lesson.reward_points,
                    'total_earned_points': user_course.earned_points,
                    'progress': {
                        'completed_lessons': completed_lessons,
                        'total_lessons': total_lessons,
                        'percentage': (completed_lessons / total_lessons) * 100,
                        'is_completed': user_course.is_completed
                    },
                    'user_balance': {
                        'coins': request.user.coins,
                        'diamonds': request.user.diamonds
                    }
                }, status=status.HTTP_200_OK)
                
            except CourseLessonModel.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Урок не найден'
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserCourseProgressView(APIView):
    """Получение прогресса пользователя по конкретному курсу (требует авторизации)"""
    
    @token_required
    def get(self, request, course_id):
        try:
            course = CourseModel.objects.get(id=course_id)
            try:
                user_course = UserCourseModel.objects.get(
                    user=request.user,
                    course=course
                )
                serializer = UserCourseSerializer(user_course)
                return Response({
                    'success': True,
                    'data': serializer.data
                })
            except UserCourseModel.DoesNotExist:
                return Response({
                    'success': True,
                    'data': {
                        'course': CourseListSerializer(course).data,
                        'earned_points': 0,
                        'is_purchased': False,
                        'is_completed': False,
                        'completed_lessons_count': 0,
                        'progress_percentage': 0
                    }
                })
        except CourseModel.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Курс не найден'
            }, status=status.HTTP_404_NOT_FOUND)


# Функциональные представления для простых операций
@api_view(['GET'])
def course_search(request):
    """Поиск курсов по названию (публичный endpoint)"""
    query = request.GET.get('q', '')
    if not query:
        return Response({
            'success': False,
            'error': 'Параметр поиска q обязателен'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    courses = CourseModel.objects.filter(
        name__icontains=query
    ).order_by('-created_at')
    
    serializer = CourseListSerializer(courses, many=True, context={'request': request})
    return Response({
        'success': True,
        'data': serializer.data,
        'count': courses.count(),
        'query': query
    })


@api_view(['GET'])
def courses_by_level(request, min_level):
    """Получение курсов по минимальному уровню (публичный endpoint)"""
    courses = CourseModel.objects.filter(
        min_level__lte=min_level
    ).order_by('min_level', '-created_at')
    
    serializer = CourseListSerializer(courses, many=True, context={'request': request})
    return Response({
        'success': True,
        'data': serializer.data,
        'count': courses.count(),
        'max_level': min_level
    })


@api_view(['GET'])
@token_required
def all_courses_with_purchase_info(request):
    """Получение всех курсов с информацией о покупке для авторизованного пользователя"""
    from .models import UserCourseModel
    
    # Получаем все курсы
    courses = CourseModel.objects.all().order_by('-created_at')
    
    # Получаем ID купленных курсов пользователя
    purchased_course_ids = set(UserCourseModel.objects.filter(
        user=request.user, 
        is_purchased=True
    ).values_list('course_id', flat=True))
    
    # Сериализуем курсы
    serializer = CourseListSerializer(courses, many=True, context={'request': request})
    courses_data = serializer.data
    
    # Добавляем информацию о покупке к каждому курсу
    for course_data in courses_data:
        course_data['is_purchased'] = course_data['id'] in purchased_course_ids
        course_data['can_purchase'] = (
            course_data['id'] not in purchased_course_ids and
            (course_data['price'] == 0 or course_data['price'] <= request.user.coins) and
            course_data['min_level'] <= request.user.level
        )
    
    return Response({
        'success': True,
        'data': courses_data,
        'count': courses.count(),
        'user_level': request.user.level,
        'user_balance': {
            'coins': request.user.coins,
            'diamonds': request.user.diamonds
        }
    })


@api_view(['GET'])
@token_required
def user_available_courses(request):
    """Получение курсов, доступных для покупки пользователем (требует авторизации)"""
    from .models import UserCourseModel
    
    # Получаем курсы, которые пользователь может купить:
    # 1. Подходят по уровню
    # 2. Пользователь может их купить (достаточно средств или бесплатные)
    # 3. Пользователь их еще не купил
    
    # Получаем ID уже купленных курсов
    purchased_course_ids = UserCourseModel.objects.filter(
        user=request.user, 
        is_purchased=True
    ).values_list('course_id', flat=True)
    
    # Фильтруем курсы
    available_courses = CourseModel.objects.filter(
        min_level__lte=request.user.level  # Подходят по уровню
    ).exclude(
        id__in=purchased_course_ids  # Исключаем уже купленные
    ).filter(
        # Либо бесплатные, либо пользователь может купить
        models.Q(price=0) | models.Q(price__lte=request.user.coins)
    ).order_by('-created_at')
    
    serializer = CourseListSerializer(available_courses, many=True, context={'request': request})
    return Response({
        'success': True,
        'data': serializer.data,
        'count': available_courses.count(),
        'user_level': request.user.level,
        'user_balance': {
            'coins': request.user.coins,
            'diamonds': request.user.diamonds
        }
    })

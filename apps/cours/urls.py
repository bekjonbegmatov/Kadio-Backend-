from django.urls import path
from . import views

app_name = 'cours'

urlpatterns = [
    # Публичные endpoints для курсов
    path('courses/', views.CourseListView.as_view(), name='course-list'),
    path('courses/<int:course_id>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('courses/<int:course_id>/lessons/', views.CourseLessonsView.as_view(), name='course-lessons'),
    path('courses/<int:course_id>/comments/', views.CourseCommentsView.as_view(), name='course-comments'),
    path('lessons/<int:lesson_id>/comments/', views.LessonCommentsView.as_view(), name='lesson-comments'),
    
    # Поиск и фильтрация курсов
    path('courses/search/', views.course_search, name='course-search'),
    path('courses/level/<int:min_level>/', views.courses_by_level, name='courses-by-level'),
    
    # Endpoints для авторизованных пользователей
    path('user/courses/', views.UserCoursesView.as_view(), name='user-courses'),
    path('user/courses/available/', views.user_available_courses, name='user-available-courses'),
    path('user/courses/<int:course_id>/progress/', views.UserCourseProgressView.as_view(), name='user-course-progress'),
    
    # Покупка курсов и завершение уроков
    path('courses/purchase/', views.CoursePurchaseView.as_view(), name='course-purchase'),
    path('lessons/complete/', views.LessonCompleteView.as_view(), name='lesson-complete'),
]
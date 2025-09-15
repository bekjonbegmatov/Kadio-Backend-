#!/usr/bin/env python
"""
Скрипт для генерации курсов по различным тематикам
"""

import os
import sys
import django
from django.utils import timezone

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from apps.cours.models import CourseModel, CourseLessonModel

def create_courses():
    """Создание курсов по различным тематикам"""
    
    courses_data = [
        # Программирование
        {
            'name': 'Основы Python для начинающих',
            'description': 'Изучите основы программирования на Python с нуля. Курс включает переменные, циклы, функции и работу с данными.',
            'price': 0,  # Бесплатный
            'min_level': 1,
            'lessons': [
                {'name': 'Введение в Python', 'description': 'Что такое Python и как его установить', 'order': 1, 'reward_points': 10},
                {'name': 'Переменные и типы данных', 'description': 'Работа с числами, строками и булевыми значениями', 'order': 2, 'reward_points': 15},
                {'name': 'Условные конструкции', 'description': 'If, elif, else - принятие решений в коде', 'order': 3, 'reward_points': 20},
                {'name': 'Циклы for и while', 'description': 'Повторение действий в программе', 'order': 4, 'reward_points': 25},
                {'name': 'Функции', 'description': 'Создание собственных функций', 'order': 5, 'reward_points': 30}
            ]
        },
        {
            'name': 'JavaScript для веб-разработки',
            'description': 'Полный курс по JavaScript от основ до продвинутых техник. DOM, события, асинхронность.',
            'price': 50,
            'min_level': 3,
            'lessons': [
                {'name': 'Основы JavaScript', 'description': 'Синтаксис, переменные, операторы', 'order': 1, 'reward_points': 15},
                {'name': 'Работа с DOM', 'description': 'Манипуляции с элементами страницы', 'order': 2, 'reward_points': 20},
                {'name': 'События и обработчики', 'description': 'Реакция на действия пользователя', 'order': 3, 'reward_points': 25},
                {'name': 'Асинхронный JavaScript', 'description': 'Promises, async/await, fetch API', 'order': 4, 'reward_points': 30}
            ]
        },
        
        # Дизайн
        {
            'name': 'UI/UX дизайн с нуля',
            'description': 'Изучите принципы пользовательского интерфейса и опыта. От теории до практических проектов.',
            'price': 40,
            'min_level': 1,
            'lessons': [
                {'name': 'Основы UI/UX', 'description': 'Что такое пользовательский интерфейс и опыт', 'order': 1, 'reward_points': 12},
                {'name': 'Принципы дизайна', 'description': 'Контраст, повторение, выравнивание, близость', 'order': 2, 'reward_points': 18},
                {'name': 'Цветовая теория', 'description': 'Психология цвета и цветовые схемы', 'order': 3, 'reward_points': 22},
                {'name': 'Типографика', 'description': 'Выбор и сочетание шрифтов', 'order': 4, 'reward_points': 25},
                {'name': 'Прототипирование', 'description': 'Создание интерактивных прототипов', 'order': 5, 'reward_points': 30}
            ]
        },
        {
            'name': 'Графический дизайн в Photoshop',
            'description': 'Профессиональная работа в Adobe Photoshop. Ретушь, коллажи, веб-дизайн.',
            'price': 200,
            'min_level': 5,
            'lessons': [
                {'name': 'Интерфейс Photoshop', 'description': 'Знакомство с рабочим пространством', 'order': 1, 'reward_points': 20},
                {'name': 'Слои и маски', 'description': 'Основа неразрушающего редактирования', 'order': 2, 'reward_points': 25},
                {'name': 'Инструменты выделения', 'description': 'Точное выделение объектов', 'order': 3, 'reward_points': 30},
                {'name': 'Цветокоррекция', 'description': 'Настройка цвета и тона изображений', 'order': 4, 'reward_points': 35}
            ]
        },
        
        # Менеджмент
        {
            'name': 'Основы проектного менеджмента',
            'description': 'Управление проектами от идеи до реализации. Agile, Scrum, планирование и контроль.',
            'price': 0,  # Бесплатный
            'min_level': 2,
            'lessons': [
                {'name': 'Что такое проект', 'description': 'Определение и характеристики проектов', 'order': 1, 'reward_points': 15},
                {'name': 'Жизненный цикл проекта', 'description': 'Этапы от инициации до закрытия', 'order': 2, 'reward_points': 20},
                {'name': 'Agile методологии', 'description': 'Гибкие подходы к управлению', 'order': 3, 'reward_points': 25},
                {'name': 'Scrum фреймворк', 'description': 'Роли, события и артефакты Scrum', 'order': 4, 'reward_points': 30}
            ]
        },
        {
            'name': 'Лидерство и управление командой',
            'description': 'Развитие лидерских качеств, мотивация сотрудников, построение эффективных команд.',
            'price': 50,
            'min_level': 4,
            'lessons': [
                {'name': 'Стили лидерства', 'description': 'Различные подходы к руководству', 'order': 1, 'reward_points': 18},
                {'name': 'Мотивация команды', 'description': 'Как вдохновлять и мотивировать людей', 'order': 2, 'reward_points': 22},
                {'name': 'Делегирование задач', 'description': 'Эффективное распределение обязанностей', 'order': 3, 'reward_points': 25},
                {'name': 'Разрешение конфликтов', 'description': 'Управление конфликтными ситуациями', 'order': 4, 'reward_points': 28}
            ]
        },
        
        # Математика
        {
            'name': 'Математический анализ',
            'description': 'Пределы, производные, интегралы. Фундаментальные основы высшей математики.',
            'price': 40,
            'min_level': 6,
            'lessons': [
                {'name': 'Пределы функций', 'description': 'Понятие предела и его вычисление', 'order': 1, 'reward_points': 25},
                {'name': 'Производные', 'description': 'Дифференцирование функций', 'order': 2, 'reward_points': 30},
                {'name': 'Интегралы', 'description': 'Неопределенные и определенные интегралы', 'order': 3, 'reward_points': 35},
                {'name': 'Применение производных', 'description': 'Исследование функций', 'order': 4, 'reward_points': 40}
            ]
        },
        {
            'name': 'Статистика и анализ данных',
            'description': 'Описательная статистика, проверка гипотез, корреляционный анализ.',
            'price': 0,  # Бесплатный
            'min_level': 3,
            'lessons': [
                {'name': 'Описательная статистика', 'description': 'Меры центральной тенденции и разброса', 'order': 1, 'reward_points': 20},
                {'name': 'Вероятность', 'description': 'Основы теории вероятностей', 'order': 2, 'reward_points': 25},
                {'name': 'Распределения', 'description': 'Нормальное и другие распределения', 'order': 3, 'reward_points': 30}
            ]
        },
        
        # Физика
        {
            'name': 'Классическая механика',
            'description': 'Законы Ньютона, кинематика, динамика. Основы физики движения.',
            'price': 50,
            'min_level': 5,
            'lessons': [
                {'name': 'Кинематика', 'description': 'Описание движения без учета причин', 'order': 1, 'reward_points': 22},
                {'name': 'Законы Ньютона', 'description': 'Три основных закона механики', 'order': 2, 'reward_points': 28},
                {'name': 'Работа и энергия', 'description': 'Кинетическая и потенциальная энергия', 'order': 3, 'reward_points': 32},
                {'name': 'Импульс', 'description': 'Закон сохранения импульса', 'order': 4, 'reward_points': 35}
            ]
        },
        
        # Психология
        {
            'name': 'Основы психологии',
            'description': 'Введение в психологию: восприятие, память, мышление, эмоции.',
            'price': 0,  # Бесплатный
            'min_level': 1,
            'lessons': [
                {'name': 'Что изучает психология', 'description': 'Предмет и методы психологии', 'order': 1, 'reward_points': 15},
                {'name': 'Восприятие и внимание', 'description': 'Как мы воспринимаем мир', 'order': 2, 'reward_points': 18},
                {'name': 'Память и забывание', 'description': 'Процессы запоминания и воспроизведения', 'order': 3, 'reward_points': 22},
                {'name': 'Эмоции и чувства', 'description': 'Эмоциональная сфера человека', 'order': 4, 'reward_points': 25}
            ]
        },
        {
            'name': 'Когнитивно-поведенческая терапия',
            'description': 'Методы КПТ для работы с тревогой, депрессией и другими расстройствами.',
            'price': 200,
            'min_level': 7,
            'lessons': [
                {'name': 'Основы КПТ', 'description': 'Принципы когнитивно-поведенческой терапии', 'order': 1, 'reward_points': 30},
                {'name': 'Когнитивные искажения', 'description': 'Выявление и коррекция мыслительных ошибок', 'order': 2, 'reward_points': 35},
                {'name': 'Поведенческие техники', 'description': 'Изменение поведенческих паттернов', 'order': 3, 'reward_points': 40}
            ]
        }
    ]
    
    created_courses = []
    
    for course_data in courses_data:
        # Создаем курс
        lessons_data = course_data.pop('lessons')
        
        course = CourseModel.objects.create(
            name=course_data['name'],
            description=course_data['description'],
            price=course_data['price'],
            min_level=course_data['min_level'],
            lessons_count=len(lessons_data),
            total_reward_points=sum(lesson['reward_points'] for lesson in lessons_data)
        )
        
        # Создаем уроки для курса
        for lesson_data in lessons_data:
            CourseLessonModel.objects.create(
                course=course,
                name=lesson_data['name'],
                description=lesson_data['description'],
                order=lesson_data['order'],
                reward_points=lesson_data['reward_points']
            )
        
        created_courses.append(course)
        print(f"✅ Создан курс: {course.name} (Цена: {course.price}, Уроков: {course.lessons_count})")
    
    return created_courses

if __name__ == '__main__':
    print("🚀 Начинаем создание курсов...")
    
    # Проверяем, есть ли уже курсы
    existing_courses = CourseModel.objects.count()
    if existing_courses > 0:
        print(f"⚠️  В базе уже есть {existing_courses} курсов. Продолжить? (y/n)")
        response = input().lower()
        if response != 'y':
            print("❌ Отменено")
            sys.exit(0)
    
    courses = create_courses()
    
    print(f"\n🎉 Успешно создано {len(courses)} курсов!")
    print("\n📊 Статистика:")
    
    free_courses = [c for c in courses if c.price == 0]
    paid_courses = [c for c in courses if c.price > 0]
    
    print(f"   • Бесплатных курсов: {len(free_courses)}")
    print(f"   • Платных курсов: {len(paid_courses)}")
    
    if paid_courses:
        avg_price = sum(c.price for c in paid_courses) / len(paid_courses)
        print(f"   • Средняя цена: {avg_price:.0f} монет")
        print(f"   • Самый дорогой: {max(c.price for c in paid_courses)} монет")
    
    total_lessons = sum(c.lessons_count for c in courses)
    total_points = sum(c.total_reward_points for c in courses)
    
    print(f"   • Всего уроков: {total_lessons}")
    print(f"   • Всего наградных очков: {total_points}")
    
    print("\n✨ Готово! Курсы добавлены в базу данных.")
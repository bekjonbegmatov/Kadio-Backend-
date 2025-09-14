#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для генерации тестовых пользователей с разнообразными профилями
Генерирует 100 пользователей из различных сфер деятельности
"""

import os
import sys
import django
import random
from datetime import datetime, timedelta
from faker import Faker

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from apps.api_auth.models import UserModel

# Инициализация Faker с русской локалью
fake = Faker(['ru_RU', 'en_US'])

class UserGenerator:
    def __init__(self):
        self.themes = {
            'it': {
                'interests': {
                    'hobby': ['Python', 'JavaScript', 'Machine Learning', 'Web Development', 'DevOps', 'Cybersecurity'],
                    'skills': ['Programming', 'System Administration', 'Database Design', 'Cloud Computing'],
                    'technologies': ['React', 'Django', 'Docker', 'Kubernetes', 'AWS', 'PostgreSQL']
                },
                'bio_templates': [
                    'Разработчик с {years} летним опытом в {tech}. Увлекаюсь {hobby}.',
                    'Senior {role} в IT компании. Специализируюсь на {tech}.',
                    'Фрилансер, создаю {projects}. Изучаю {learning}.',
                    'Tech Lead с опытом в {tech}. Люблю делиться знаниями.'
                ],
                'roles': ['Developer', 'DevOps Engineer', 'Data Scientist', 'Frontend Developer', 'Backend Developer']
            },
            'medicine': {
                'interests': {
                    'specialty': ['Кардиология', 'Неврология', 'Педиатрия', 'Хирургия', 'Терапия', 'Стоматология'],
                    'hobby': ['Медицинские исследования', 'Здоровый образ жизни', 'Йога', 'Бег', 'Чтение'],
                    'skills': ['Диагностика', 'Лечение', 'Профилактика', 'Консультирование']
                },
                'bio_templates': [
                    'Врач-{specialty} с {years} летним стажем. Помогаю людям быть здоровыми.',
                    'Медицинский работник, специализируюсь на {specialty}.',
                    'Практикующий врач. Увлекаюсь {hobby} в свободное время.',
                    'Доктор медицинских наук. Область интересов: {specialty}.'
                ]
            },
            'education': {
                'interests': {
                    'subjects': ['Математика', 'Физика', 'История', 'Литература', 'Биология', 'Химия'],
                    'methods': ['Интерактивное обучение', 'Проектная деятельность', 'Дистанционное образование'],
                    'hobby': ['Чтение', 'Путешествия', 'Театр', 'Музыка', 'Рисование']
                },
                'bio_templates': [
                    'Преподаватель {subject} с {years} летним опытом. Люблю {hobby}.',
                    'Учитель в школе. Специализируюсь на {subject}.',
                    'Педагог-новатор. Применяю {methods} в обучении.',
                    'Заведующий кафедрой {subject}. Автор учебных пособий.'
                ]
            },
            'business': {
                'interests': {
                    'areas': ['Маркетинг', 'Продажи', 'Управление', 'Финансы', 'Стратегия', 'HR'],
                    'skills': ['Лидерство', 'Переговоры', 'Аналитика', 'Планирование'],
                    'hobby': ['Гольф', 'Теннис', 'Чтение бизнес-литературы', 'Нетворкинг']
                },
                'bio_templates': [
                    'Руководитель отдела {area}. {years} лет в бизнесе.',
                    'Предприниматель и основатель стартапа в сфере {area}.',
                    'Бизнес-консультант. Специализируюсь на {area}.',
                    'Топ-менеджер с опытом в {area}. Увлекаюсь {hobby}.'
                ]
            },
            'creative': {
                'interests': {
                    'arts': ['Живопись', 'Фотография', 'Дизайн', 'Музыка', 'Театр', 'Кино'],
                    'styles': ['Современное искусство', 'Классика', 'Авангард', 'Минимализм'],
                    'hobby': ['Выставки', 'Концерты', 'Мастер-классы', 'Творческие встречи']
                },
                'bio_templates': [
                    'Художник, работаю в стиле {style}. Специализируюсь на {art}.',
                    'Творческая личность. Увлекаюсь {art} уже {years} лет.',
                    'Дизайнер и {art}. Люблю экспериментировать.',
                    'Преподаю {art} и создаю авторские работы.'
                ]
            },
            'sports': {
                'interests': {
                    'sports': ['Футбол', 'Баскетбол', 'Теннис', 'Плавание', 'Бег', 'Фитнес', 'Йога'],
                    'activities': ['Тренировки', 'Соревнования', 'Здоровый образ жизни'],
                    'hobby': ['Спортивное питание', 'Мотивация', 'Командная работа']
                },
                'bio_templates': [
                    'Профессиональный спортсмен в {sport}. Тренируюсь {years} лет.',
                    'Тренер по {sport}. Помогаю достигать спортивных целей.',
                    'Фитнес-инструктор. Специализируюсь на {sport}.',
                    'Любитель активного образа жизни. Увлекаюсь {sport}.'
                ]
            },
            'science': {
                'interests': {
                    'fields': ['Физика', 'Химия', 'Биология', 'Математика', 'Астрономия', 'Геология'],
                    'research': ['Исследования', 'Эксперименты', 'Публикации', 'Конференции'],
                    'hobby': ['Научная литература', 'Лекции', 'Музеи', 'Документальные фильмы']
                },
                'bio_templates': [
                    'Ученый-исследователь в области {field}. {years} лет в науке.',
                    'Кандидат наук по {field}. Занимаюсь {research}.',
                    'Научный сотрудник. Специализируюсь на {field}.',
                    'Преподаватель и исследователь {field}. Автор {publications} публикаций.'
                ]
            }
        }
        
        self.usernames_used = set()
        self.emails_used = set()
    
    def generate_unique_username(self, theme=None):
        """Генерирует уникальное имя пользователя"""
        attempts = 0
        while attempts < 100:
            if theme == 'it':
                username = random.choice([
                    f"dev_{fake.user_name()}",
                    f"code_{fake.user_name()}",
                    f"{fake.user_name()}_dev",
                    f"tech_{fake.user_name()}"
                ])
            elif theme == 'medicine':
                username = random.choice([
                    f"dr_{fake.user_name()}",
                    f"med_{fake.user_name()}",
                    f"{fake.user_name()}_md"
                ])
            else:
                username = fake.user_name()
            
            username = username.lower().replace('.', '_')
            if username not in self.usernames_used:
                self.usernames_used.add(username)
                return username
            attempts += 1
        
        # Если не удалось сгенерировать уникальное имя
        return f"user_{random.randint(10000, 99999)}"
    
    def generate_unique_email(self):
        """Генерирует уникальный email"""
        attempts = 0
        while attempts < 100:
            email = fake.email()
            if email not in self.emails_used:
                self.emails_used.add(email)
                return email
            attempts += 1
        
        return f"user{random.randint(10000, 99999)}@example.com"
    
    def generate_bio(self, theme_data, theme_name):
        """Генерирует биографию на основе темы"""
        template = random.choice(theme_data['bio_templates'])
        
        replacements = {
            'years': random.randint(1, 15),
            'publications': random.randint(5, 50)
        }
        
        # Добавляем специфичные для темы замены
        for category, items in theme_data['interests'].items():
            if category in template:
                replacements[category] = random.choice(items)
        
        # Специальные замены для разных тем
        if theme_name == 'it':
            replacements.update({
                'tech': random.choice(theme_data['interests']['technologies']),
                'role': random.choice(theme_data['roles']),
                'projects': random.choice(['веб-приложения', 'мобильные приложения', 'API']),
                'learning': random.choice(['новые технологии', 'архитектуру', 'алгоритмы'])
            })
        elif theme_name == 'medicine':
            replacements['specialty'] = random.choice(theme_data['interests']['specialty'])
        elif theme_name == 'education':
            replacements['subject'] = random.choice(theme_data['interests']['subjects'])
            replacements['methods'] = random.choice(theme_data['interests']['methods'])
        elif theme_name == 'business':
            replacements['area'] = random.choice(theme_data['interests']['areas'])
        elif theme_name == 'creative':
            replacements['art'] = random.choice(theme_data['interests']['arts'])
            replacements['style'] = random.choice(theme_data['interests']['styles'])
        elif theme_name == 'sports':
            replacements['sport'] = random.choice(theme_data['interests']['sports'])
        elif theme_name == 'science':
            replacements['field'] = random.choice(theme_data['interests']['fields'])
            replacements['research'] = random.choice(theme_data['interests']['research'])
        
        try:
            return template.format(**replacements)
        except KeyError:
            return template
    
    def generate_interests(self, theme_data, completeness='full'):
        """Генерирует интересы пользователя"""
        if completeness == 'minimal':
            # Минимальные интересы
            category = random.choice(list(theme_data['interests'].keys()))
            items = random.sample(theme_data['interests'][category], 
                                min(2, len(theme_data['interests'][category])))
            return {category: items}
        elif completeness == 'partial':
            # Частичные интересы
            interests = {}
            categories = random.sample(list(theme_data['interests'].keys()), 
                                     random.randint(1, 2))
            for category in categories:
                items = random.sample(theme_data['interests'][category],
                                    random.randint(1, min(3, len(theme_data['interests'][category]))))
                interests[category] = items
            return interests
        else:
            # Полные интересы
            interests = {}
            for category, items in theme_data['interests'].items():
                selected_items = random.sample(items, random.randint(2, min(4, len(items))))
                interests[category] = selected_items
            return interests
    
    def generate_user(self, theme_name=None, completeness='full'):
        """Генерирует одного пользователя"""
        if not theme_name:
            theme_name = random.choice(list(self.themes.keys()))
        
        theme_data = self.themes[theme_name]
        
        # Базовые данные
        username = self.generate_unique_username(theme_name)
        email = self.generate_unique_email()
        full_name = fake.name()
        
        # Уровень заполненности профиля
        if completeness == 'minimal':
            bio = None
            interests = {}
            level = random.randint(0, 3)
            link = None
            date_of_birth = None
        elif completeness == 'partial':
            bio = self.generate_bio(theme_data, theme_name) if random.choice([True, False]) else None
            interests = self.generate_interests(theme_data, 'partial')
            level = random.randint(1, 8)
            link = fake.url() if random.choice([True, False]) else None
            date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=65) if random.choice([True, False]) else None
        else:  # full
            bio = self.generate_bio(theme_data, theme_name)
            interests = self.generate_interests(theme_data, 'full')
            level = random.randint(5, 25)
            link = fake.url()
            date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=65)
        
        # Создание пользователя
        user = UserModel(
            username=username,
            email=email,
            full_name=full_name,
            bio=bio,
            interests=interests,
            level=level,
            link=link,
            date_of_birth=date_of_birth,
            streak_days=random.randint(0, level * 2) if level > 0 else 0,
            diamonds=random.randint(0, 1000),
            coins=random.randint(0, 5000),
            user_time_zone=random.choice(['Europe/Moscow', 'Europe/Kiev', 'Asia/Almaty', 'UTC']),
            last_active=fake.date_time_between(start_date='-30d', end_date='now') if random.choice([True, False]) else None,
            is_active=random.choice([True, True, True, False])  # 75% активных
        )
        
        # Устанавливаем пароль
        user.set_password('testpassword123')
        user.generate_token()
        
        return user, theme_name
    
    def generate_bulk_users(self, count=100):
        """Генерирует множество пользователей"""
        users = []
        themes_distribution = {
            'it': 20,
            'medicine': 15,
            'education': 15,
            'business': 15,
            'creative': 12,
            'sports': 12,
            'science': 11
        }
        
        completeness_distribution = {
            'full': 60,      # 60% полностью заполненных
            'partial': 30,   # 30% частично заполненных
            'minimal': 10    # 10% минимально заполненных
        }
        
        print(f"🚀 Начинаю генерацию {count} пользователей...")
        
        for i in range(count):
            # Выбираем тему на основе распределения
            theme_choices = []
            for theme, percentage in themes_distribution.items():
                theme_choices.extend([theme] * percentage)
            
            theme = random.choice(theme_choices)
            
            # Выбираем уровень заполненности
            completeness_choices = []
            for comp, percentage in completeness_distribution.items():
                completeness_choices.extend([comp] * percentage)
            
            completeness = random.choice(completeness_choices)
            
            try:
                user, user_theme = self.generate_user(theme, completeness)
                users.append((user, user_theme, completeness))
                
                if (i + 1) % 10 == 0:
                    print(f"✅ Сгенерировано {i + 1}/{count} пользователей")
                    
            except Exception as e:
                print(f"❌ Ошибка при генерации пользователя {i + 1}: {e}")
                continue
        
        return users
    
    def save_users(self, users):
        """Сохраняет пользователей в базу данных"""
        print("💾 Сохраняю пользователей в базу данных...")
        
        saved_count = 0
        theme_stats = {}
        completeness_stats = {'full': 0, 'partial': 0, 'minimal': 0}
        
        for user, theme, completeness in users:
            try:
                user.save()
                saved_count += 1
                
                # Статистика по темам
                theme_stats[theme] = theme_stats.get(theme, 0) + 1
                completeness_stats[completeness] += 1
                
            except Exception as e:
                print(f"❌ Ошибка при сохранении пользователя {user.username}: {e}")
                continue
        
        print(f"\n🎉 Успешно создано {saved_count} пользователей!")
        print("\n📊 Статистика по темам:")
        for theme, count in theme_stats.items():
            print(f"  {theme}: {count} пользователей")
        
        print("\n📈 Статистика по заполненности:")
        for comp, count in completeness_stats.items():
            print(f"  {comp}: {count} пользователей")
        
        return saved_count

def main():
    """Основная функция"""
    print("🎭 Генератор разнообразных пользователей")
    print("=" * 50)
    
    # Проверяем, есть ли уже пользователи
    existing_users = UserModel.objects.count()
    if existing_users > 0:
        print(f"⚠️  В базе данных уже есть {existing_users} пользователей.")
        response = input("Продолжить генерацию? (y/n): ")
        if response.lower() != 'y':
            print("❌ Генерация отменена.")
            return
    
    generator = UserGenerator()
    
    try:
        # Генерируем пользователей
        users = generator.generate_bulk_users(100)
        
        if not users:
            print("❌ Не удалось сгенерировать пользователей.")
            return
        
        # Сохраняем в базу данных
        saved_count = generator.save_users(users)
        
        print(f"\n✨ Генерация завершена! Создано {saved_count} пользователей.")
        print("\n🔐 Все пользователи имеют пароль: testpassword123")
        print("\n📝 Примеры созданных пользователей:")
        
        # Показываем несколько примеров
        sample_users = UserModel.objects.order_by('-id')[:5]
        for user in sample_users:
            print(f"  👤 {user.username} ({user.email}) - Уровень: {user.level}")
            if user.bio:
                print(f"     📖 {user.bio[:100]}...")
            print(f"     🎯 Интересы: {list(user.interests.keys()) if user.interests else 'Не указаны'}")
            print()
        
    except KeyboardInterrupt:
        print("\n⏹️  Генерация прервана пользователем.")
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
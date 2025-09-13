#!/usr/bin/env python3
"""
Скрипт для массовой генерации данных активности пользователей
Использование: python3 generate_activities_bulk.py
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# Настройка Django окружения
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
sys.path.append('/Users/behruz/Documents/Kadio-Backend-')
django.setup()

from django.utils import timezone
from apps.api_auth.models import UserModel
from apps.user_activitys.models import UserActivity


def generate_realistic_activities(count=5000, clear_existing=False):
    """
    Генерирует реалистичные данные активности пользователей
    
    Args:
        count (int): Количество записей для генерации
        clear_existing (bool): Очистить существующие данные
    """
    print(f"🚀 Начинаем генерацию {count} записей активности пользователей...")
    
    # Очистка существующих данных если указано
    if clear_existing:
        existing_count = UserActivity.objects.count()
        UserActivity.objects.all().delete()
        print(f"🗑️  Удалено {existing_count} существующих записей активности")
    
    # Получаем всех пользователей
    users = list(UserModel.objects.all())
    if not users:
        print("❌ В базе данных нет пользователей. Создайте пользователей сначала.")
        return
    
    print(f"👥 Найдено {len(users)} пользователей в системе")
    
    # Определяем временной диапазон - текущий месяц
    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
    
    print(f"📅 Период генерации: {start_of_month.strftime('%d.%m.%Y')} - {end_of_month.strftime('%d.%m.%Y')}")
    
    # Расширенный список действий с весами (более частые действия имеют больший вес)
    weighted_actions = [
        # Частые действия (вес 10)
        ('Вошел в систему', 10),
        ('Просмотрел профиль', 8),
        ('Просмотрел уведомления', 7),
        ('Вышел из системы', 9),
        
        # Средние по частоте действия (вес 5)
        ('Обновил настройки', 5),
        ('Просмотрел активность', 5),
        ('Отметил уведомление как прочитанное', 6),
        ('Просмотрел статистику', 4),
        ('Увеличил серию дней', 3),
        
        # Редкие действия (вес 2)
        ('Загрузил аватар', 2),
        ('Изменил пароль', 2),
        ('Обновил биографию', 2),
        ('Изменил часовой пояс', 1),
        ('Получил новый значок', 3),
        ('Обновил интересы', 2),
        
        # Очень редкие действия (вес 1)
        ('Изменил email', 1),
        ('Подтвердил email', 1),
        ('Восстановил пароль', 1),
        ('Экспортировал данные', 1),
        ('Создал резервную копию', 1),
        
        # Дополнительные реалистичные действия
        ('Просмотрел ленту новостей', 6),
        ('Поставил лайк', 8),
        ('Оставил комментарий', 4),
        ('Поделился контентом', 3),
        ('Добавил в избранное', 4),
        ('Выполнил поиск', 5),
        ('Просмотрел рекомендации', 4),
        ('Обновил статус', 3),
        ('Присоединился к группе', 2),
        ('Покинул группу', 1),
        ('Отправил сообщение', 6),
        ('Прочитал сообщение', 7),
        ('Просмотрел галерею', 3),
        ('Загрузил фото', 2),
        ('Удалил фото', 1),
        ('Изменил приватность', 1),
        ('Заблокировал пользователя', 1),
        ('Разблокировал пользователя', 1),
        ('Подписался на уведомления', 2),
        ('Отписался от уведомлений', 1),
    ]
    
    # Создаем список действий с учетом весов
    actions_pool = []
    for action, weight in weighted_actions:
        actions_pool.extend([action] * weight)
    
    # Генерируем активности с более реалистичным распределением по времени
    activities_to_create = []
    user_daily_activities = {}  # Отслеживаем активность пользователей по дням
    
    print("⏳ Генерируем записи активности...")
    
    for i in range(count):
        # Выбираем пользователя с учетом их "активности"
        # Некоторые пользователи более активны чем другие
        if random.random() < 0.3:  # 30% шанс выбрать "супер активного" пользователя
            user = random.choice(users[:min(3, len(users))])  # Первые 3 пользователя более активны
        else:
            user = random.choice(users)
        
        # Выбираем действие с учетом весов
        action = random.choice(actions_pool)
        
        # Генерируем более реалистичное время
        # Больше активности в рабочие часы (9-18) и меньше ночью (0-6)
        random_day = random.randint(0, (end_of_month - start_of_month).days)
        base_date = start_of_month + timedelta(days=random_day)
        
        # Распределение по часам (больше активности днем)
        hour_weights = {
            range(0, 6): 1,    # Ночь - низкая активность
            range(6, 9): 3,    # Утро - средняя активность
            range(9, 12): 8,   # Утро рабочее - высокая активность
            range(12, 14): 6,  # Обед - средняя активность
            range(14, 18): 9,  # День рабочий - очень высокая активность
            range(18, 21): 7,  # Вечер - высокая активность
            range(21, 24): 4,  # Поздний вечер - средняя активность
        }
        
        # Выбираем час с учетом весов
        hour_pool = []
        for hour_range, weight in hour_weights.items():
            for hour in hour_range:
                hour_pool.extend([hour] * weight)
        
        hour = random.choice(hour_pool)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        
        random_timestamp = base_date.replace(hour=hour, minute=minute, second=second)
        
        # Создаем объект активности
        activity = UserActivity(
            user=user,
            action=action,
            timestamp=random_timestamp
        )
        activities_to_create.append(activity)
        
        # Отслеживаем статистику
        day_key = random_timestamp.date()
        if day_key not in user_daily_activities:
            user_daily_activities[day_key] = set()
        user_daily_activities[day_key].add(user.username)
        
        # Показываем прогресс
        if (i + 1) % 500 == 0:
            print(f"📊 Создано {i + 1}/{count} записей ({((i + 1)/count*100):.1f}%)")
    
    # Массовое создание записей
    print("💾 Сохраняем данные в базу...")
    UserActivity.objects.bulk_create(activities_to_create, batch_size=1000)
    
    print(f"✅ Успешно создано {count} записей активности!")
    
    # Показываем детальную статистику
    print("\n📈 СТАТИСТИКА ГЕНЕРАЦИИ:")
    print("=" * 50)
    
    # Статистика по пользователям
    user_stats = {}
    for activity in activities_to_create:
        username = activity.user.username
        user_stats[username] = user_stats.get(username, 0) + 1
    
    print(f"\n👥 Активность по пользователям ({len(user_stats)} пользователей):")
    for username, activity_count in sorted(user_stats.items(), key=lambda x: x[1], reverse=True):
        percentage = (activity_count / count) * 100
        print(f"  📊 {username}: {activity_count} активностей ({percentage:.1f}%)")
    
    # Статистика по действиям
    action_stats = {}
    for activity in activities_to_create:
        action = activity.action
        action_stats[action] = action_stats.get(action, 0) + 1
    
    print(f"\n🎯 Топ-15 самых частых действий:")
    sorted_actions = sorted(action_stats.items(), key=lambda x: x[1], reverse=True)[:15]
    for i, (action, action_count) in enumerate(sorted_actions, 1):
        percentage = (action_count / count) * 100
        print(f"  {i:2d}. {action}: {action_count} раз ({percentage:.1f}%)")
    
    # Статистика по дням
    daily_stats = {}
    for activity in activities_to_create:
        day = activity.timestamp.date()
        daily_stats[day] = daily_stats.get(day, 0) + 1
    
    print(f"\n📅 Активность по дням (топ-10):")
    sorted_days = sorted(daily_stats.items(), key=lambda x: x[1], reverse=True)[:10]
    for day, day_count in sorted_days:
        print(f"  📆 {day.strftime('%d.%m.%Y')}: {day_count} активностей")
    
    # Статистика по часам
    hourly_stats = {}
    for activity in activities_to_create:
        hour = activity.timestamp.hour
        hourly_stats[hour] = hourly_stats.get(hour, 0) + 1
    
    print(f"\n🕐 Распределение по часам:")
    for hour in sorted(hourly_stats.keys()):
        count_hour = hourly_stats[hour]
        bar = "█" * (count_hour // 20)  # Простая визуализация
        print(f"  {hour:2d}:00 - {count_hour:4d} активностей {bar}")
    
    print("\n🎉 Генерация завершена успешно!")
    print(f"📊 Общее количество записей в базе: {UserActivity.objects.count()}")


if __name__ == "__main__":
    print("🎯 Скрипт генерации активности пользователей")
    print("=" * 50)
    
    # Можно изменить параметры здесь
    COUNT = 2000  # Количество записей для генерации
    CLEAR_EXISTING = False  # Очистить существующие данные
    
    try:
        generate_realistic_activities(count=COUNT, clear_existing=CLEAR_EXISTING)
    except KeyboardInterrupt:
        print("\n⚠️  Генерация прервана пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка при генерации: {e}")
        import traceback
        traceback.print_exc()
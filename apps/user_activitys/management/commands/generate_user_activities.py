from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random
from apps.api_auth.models import UserModel
from apps.user_activitys.models import UserActivity


class Command(BaseCommand):
    help = 'Генерирует случайные данные активности пользователей за текущий месяц'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=1000,
            help='Количество записей активности для генерации (по умолчанию: 1000)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить существующие данные активности перед генерацией'
        )

    def handle(self, *args, **options):
        count = options['count']
        clear_existing = options['clear']

        # Очистка существующих данных если указано
        if clear_existing:
            UserActivity.objects.all().delete()
            self.stdout.write(
                self.style.WARNING('Все существующие данные активности удалены.')
            )

        # Получаем всех пользователей
        users = list(UserModel.objects.all())
        if not users:
            self.stdout.write(
                self.style.ERROR('В базе данных нет пользователей. Создайте пользователей сначала.')
            )
            return

        # Определяем временной диапазон - текущий месяц
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)

        # Список возможных действий пользователей
        actions = [
            'Вошел в систему',
            'Просмотрел профиль',
            'Обновил настройки',
            'Загрузил аватар',
            'Изменил пароль',
            'Просмотрел уведомления',
            'Отметил уведомление как прочитанное',
            'Обновил биографию',
            'Изменил часовой пояс',
            'Просмотрел список значков',
            'Получил новый значок',
            'Обновил интересы',
            'Просмотрел активность',
            'Выполнил поиск',
            'Обновил уровень',
            'Увеличил серию дней',
            'Сбросил серию дней',
            'Просмотрел статистику',
            'Экспортировал данные',
            'Изменил email',
            'Подтвердил email',
            'Восстановил пароль',
            'Вышел из системы',
            'Создал резервную копию',
            'Удалил старые данные',
            'Синхронизировал данные',
            'Просмотрел историю',
            'Обновил предпочтения',
            'Изменил тему оформления',
            'Настроил уведомления'
        ]

        # Генерируем случайные записи активности
        activities_to_create = []
        
        self.stdout.write(f'Генерация {count} записей активности...')
        
        for i in range(count):
            # Выбираем случайного пользователя
            user = random.choice(users)
            
            # Выбираем случайное действие
            action = random.choice(actions)
            
            # Генерируем случайную дату в пределах текущего месяца
            random_timestamp = start_of_month + timedelta(
                seconds=random.randint(0, int((end_of_month - start_of_month).total_seconds()))
            )
            
            # Создаем объект активности
            activity = UserActivity(
                user=user,
                action=action,
                timestamp=random_timestamp
            )
            activities_to_create.append(activity)
            
            # Показываем прогресс каждые 100 записей
            if (i + 1) % 100 == 0:
                self.stdout.write(f'Создано {i + 1} записей...')

        # Массовое создание записей для повышения производительности
        UserActivity.objects.bulk_create(activities_to_create)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Успешно создано {count} записей активности для {len(users)} пользователей '
                f'за период с {start_of_month.strftime("%d.%m.%Y")} по {end_of_month.strftime("%d.%m.%Y")}'
            )
        )
        
        # Показываем статистику по пользователям
        user_stats = {}
        for activity in activities_to_create:
            username = activity.user.username
            if username not in user_stats:
                user_stats[username] = 0
            user_stats[username] += 1
        
        self.stdout.write('\nСтатистика по пользователям:')
        for username, activity_count in sorted(user_stats.items()):
            self.stdout.write(f'  {username}: {activity_count} активностей')
        
        # Показываем статистику по действиям
        action_stats = {}
        for activity in activities_to_create:
            action = activity.action
            if action not in action_stats:
                action_stats[action] = 0
            action_stats[action] += 1
        
        self.stdout.write('\nТоп-10 самых частых действий:')
        sorted_actions = sorted(action_stats.items(), key=lambda x: x[1], reverse=True)[:10]
        for action, action_count in sorted_actions:
            self.stdout.write(f'  {action}: {action_count} раз')
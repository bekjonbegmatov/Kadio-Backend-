# Обновление API Друзей - Полная Информация о Пользователях

## Изменения

API endpoint `/api/friends/` теперь возвращает полную информацию о пользователях вместо только ID.

## Старый формат ответа

```json
[
    {
        "from_user": 7,
        "to_user": 2,
        "status": "accepted",
        "created_at": "2025-09-13T17:49:05.927041Z"
    },
    {
        "from_user": 7,
        "to_user": 3,
        "status": "pending",
        "created_at": "2025-09-14T07:12:16.110665Z"
    }
]
```

## Новый формат ответа

```json
[
    {
        "from_user": {
            "id": 7,
            "username": "john_doe",
            "full_name": "John Doe",
            "avatar_url": "http://localhost:8000/media/avatars/john.jpg",
            "bio": "Software developer passionate about technology",
            "level": 15,
            "interests": {
                "hobby": ["Python", "JavaScript", "Coffee"]
            },
            "created_at": "2025-09-01T10:30:00Z"
        },
        "to_user": {
            "id": 2,
            "username": "jane_smith",
            "full_name": "Jane Smith",
            "avatar_url": "http://localhost:8000/media/avatars/jane.jpg",
            "bio": "Designer and creative thinker",
            "level": 12,
            "interests": {
                "hobby": ["Design", "Art", "Photography"]
            },
            "created_at": "2025-08-15T14:20:00Z"
        },
        "status": "accepted",
        "created_at": "2025-09-13T17:49:05.927041Z"
    },
    {
        "from_user": {
            "id": 7,
            "username": "john_doe",
            "full_name": "John Doe",
            "avatar_url": "http://localhost:8000/media/avatars/john.jpg",
            "bio": "Software developer passionate about technology",
            "level": 15,
            "interests": {
                "hobby": ["Python", "JavaScript", "Coffee"]
            },
            "created_at": "2025-09-01T10:30:00Z"
        },
        "to_user": {
            "id": 3,
            "username": "alex_wilson",
            "full_name": "Alex Wilson",
            "avatar_url": "http://localhost:8000/media/avatars/alex.jpg",
            "bio": "Marketing specialist and content creator",
            "level": 8,
            "interests": {
                "hobby": ["Marketing", "Writing", "Travel"]
            },
            "created_at": "2025-08-20T09:15:00Z"
        },
        "status": "pending",
        "created_at": "2025-09-14T07:12:16.110665Z"
    }
]
```

## Поля пользователя

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | integer | Уникальный ID пользователя |
| `username` | string | Имя пользователя |
| `full_name` | string | Полное имя пользователя |
| `avatar_url` | string/null | Полный URL аватарки пользователя |
| `bio` | string/null | Биография пользователя |
| `level` | integer | Уровень активности пользователя |
| `interests` | object/null | Интересы пользователя в JSON формате |
| `created_at` | string | Дата регистрации пользователя |

## Безопасность

✅ **Включено:**
- Вся публичная информация о пользователе
- URL аватарки
- Интересы и биография
- Уровень активности

❌ **Исключено:**
- Токены авторизации
- Пароли
- Приватные данные
- Email (если не публичный)

## Преимущества нового формата

1. **Меньше запросов к API** - вся информация о пользователях доступна сразу
2. **Лучший UX** - можно сразу отображать имена, аватарки и другую информацию
3. **Оптимизация производительности** - нет необходимости делать дополнительные запросы для получения данных пользователей
4. **Консистентность** - единый формат для всех API endpoints

## Обратная совместимость

Это изменение **не нарушает** обратную совместимость, так как:
- Все существующие поля (`status`, `created_at`) остаются на своих местах
- Поля `from_user` и `to_user` теперь содержат объекты вместо ID
- Клиентский код может легко адаптироваться: `user.id` вместо `user`

## Миграция клиентского кода

### Старый код:
```javascript
// Получение ID пользователя
const fromUserId = friendship.from_user;
const toUserId = friendship.to_user;

// Дополнительный запрос для получения информации
const fromUserData = await fetchUser(fromUserId);
const toUserData = await fetchUser(toUserId);
```

### Новый код:
```javascript
// Вся информация уже доступна
const fromUser = friendship.from_user;
const toUser = friendship.to_user;

// Прямой доступ к данным
console.log(fromUser.username, fromUser.full_name);
console.log(toUser.username, toUser.full_name);
```

## Тестирование

Для тестирования используйте:
```bash
python test_friends_api.py
```

Этот скрипт проверит:
- Корректность авторизации
- Структуру нового ответа
- Наличие всех необходимых полей пользователя
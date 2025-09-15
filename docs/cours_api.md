# Kadio Courses API Documentation

## Обзор

API для работы с курсами в системе Kadio. Предоставляет endpoints для получения информации о курсах, управления пользовательским прогрессом, покупки курсов и работы с комментариями.

## Базовый URL

```
/api/cours/
```

## Аутентификация

Для endpoints, требующих авторизации, используется токен в заголовке:

```
Authorization: Token <your_token_here>
```

## Формат ответов

Все ответы возвращаются в формате JSON со следующей структурой:

### Успешный ответ
```json
{
    "success": true,
    "data": {...},
    "count": 10,
    "message": "Операция выполнена успешно"
}
```

### Ответ с ошибкой
```json
{
    "success": false,
    "error": "Описание ошибки",
    "errors": {
        "field_name": ["Список ошибок поля"]
    }
}
```

## Endpoints

### 1. Получение списка курсов

**GET** `/courses/`

**Описание:** Получение списка всех доступных курсов (публичный endpoint)

**Параметры:** Нет

**Пример ответа:**
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "name": "Python для начинающих",
            "description": "Изучите основы программирования на Python",
            "image": "http://example.com/media/courses/python.jpg",
            "price_coins": 100,
            "price_diamonds": 10,
            "min_level": 1,
            "lessons_count": 15,
            "total_duration": 450,
            "total_reward_points": 300,
            "is_published": true,
            "created_at": "2024-01-15T10:30:00Z"
        }
    ],
    "count": 1
}
```

### 2. Получение детальной информации о курсе

**GET** `/courses/{course_id}/`

**Описание:** Получение подробной информации о конкретном курсе (публичный endpoint)

**Параметры:**
- `course_id` (int) - ID курса

**Пример ответа:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "name": "Python для начинающих",
        "description": "# Изучите основы программирования на Python\n\n## Что вы изучите:\n- Переменные и типы данных\n- Условия и циклы\n- Функции и классы",
        "image": "http://example.com/media/courses/python.jpg",
        "price_coins": 100,
        "price_diamonds": 10,
        "min_level": 1,
        "lessons_count": 15,
        "total_duration": 450,
        "total_reward_points": 300,
        "is_published": true,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    }
}
```

### 3. Получение уроков курса

**GET** `/courses/{course_id}/lessons/`

**Описание:** Получение списка уроков конкретного курса (публичный endpoint)

**Параметры:**
- `course_id` (int) - ID курса

**Пример ответа:**
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "name": "Введение в Python",
            "content": "# Урок 1: Введение\n\nДобро пожаловать в мир Python!",
            "order": 1,
            "duration_minutes": 30,
            "reward_points": 20,
            "video_url": "https://youtube.com/watch?v=example",
            "is_published": true,
            "created_at": "2024-01-15T10:30:00Z"
        }
    ],
    "count": 1
}
```

### 4. Получение комментариев к курсу

**GET** `/courses/{course_id}/comments/`

**Описание:** Получение комментариев к курсу (публичный endpoint)

**Параметры:**
- `course_id` (int) - ID курса

**Пример ответа:**
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "user": {
                "id": 1,
                "username": "john_doe",
                "level": 5
            },
            "content": "Отличный курс! Очень понятно объяснено.",
            "created_at": "2024-01-15T10:30:00Z"
        }
    ],
    "count": 1
}
```

### 5. Создание комментария к курсу

**POST** `/courses/{course_id}/comments/`

**Описание:** Создание нового комментария к курсу (требует авторизации)

**Параметры:**
- `course_id` (int) - ID курса

**Тело запроса:**
```json
{
    "content": "Текст комментария"
}
```

**Пример ответа:**
```json
{
    "success": true,
    "data": {
        "id": 2,
        "user": {
            "id": 1,
            "username": "john_doe",
            "level": 5
        },
        "content": "Текст комментария",
        "created_at": "2024-01-15T11:00:00Z"
    },
    "message": "Комментарий успешно добавлен"
}
```

### 6. Получение комментариев к уроку

**GET** `/lessons/{lesson_id}/comments/`

**Описание:** Получение комментариев к уроку (публичный endpoint)

**Параметры:**
- `lesson_id` (int) - ID урока

**Пример ответа:** Аналогично комментариям к курсу

### 7. Создание комментария к уроку

**POST** `/lessons/{lesson_id}/comments/`

**Описание:** Создание нового комментария к уроку (требует авторизации)

**Параметры:**
- `lesson_id` (int) - ID урока

**Тело запроса:**
```json
{
    "content": "Текст комментария к уроку"
}
```

### 8. Получение курсов пользователя

**GET** `/user/courses/`

**Описание:** Получение курсов, на которые записан пользователь (требует авторизации)

**Пример ответа:**
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "course": {
                "id": 1,
                "name": "Python для начинающих",
                "image": "http://example.com/media/courses/python.jpg"
            },
            "earned_points": 120,
            "is_purchased": true,
            "is_completed": false,
            "completed_lessons_count": 8,
            "progress_percentage": 53.3,
            "created_at": "2024-01-15T10:30:00Z",
            "completion_date": null
        }
    ],
    "count": 1
}
```

### 9. Покупка курса

**POST** `/courses/purchase/`

**Описание:** Покупка курса пользователем (требует авторизации)

**Тело запроса:**
```json
{
    "course_id": 1
}
```

**Пример успешного ответа:**
```json
{
    "success": true,
    "message": "Курс успешно куплен",
    "user_balance": {
        "coins": 450,
        "diamonds": 25
    }
}
```

**Пример ответа с ошибкой:**
```json
{
    "success": false,
    "error": "Недостаточно монет для покупки курса"
}
```

### 10. Завершение урока

**POST** `/lessons/complete/`

**Описание:** Отметка урока как завершенного (требует авторизации)

**Тело запроса:**
```json
{
    "lesson_id": 1
}
```

**Пример ответа:**
```json
{
    "success": true,
    "message": "Урок успешно завершен",
    "earned_points": 20,
    "total_earned_points": 140,
    "progress": {
        "completed_lessons": 9,
        "total_lessons": 15,
        "percentage": 60.0,
        "is_completed": false
    },
    "user_balance": {
        "coins": 470,
        "diamonds": 25
    }
}
```

### 11. Получение прогресса по курсу

**GET** `/user/courses/{course_id}/progress/`

**Описание:** Получение прогресса пользователя по конкретному курсу (требует авторизации)

**Параметры:**
- `course_id` (int) - ID курса

**Пример ответа:**
```json
{
    "success": true,
    "data": {
        "course": {
            "id": 1,
            "name": "Python для начинающих"
        },
        "earned_points": 140,
        "is_purchased": true,
        "is_completed": false,
        "completed_lessons_count": 9,
        "progress_percentage": 60.0
    }
}
```

### 12. Поиск курсов

**GET** `/courses/search/?q={query}`

**Описание:** Поиск курсов по названию (публичный endpoint)

**Параметры:**
- `q` (string) - Поисковый запрос

**Пример запроса:** `/courses/search/?q=python`

**Пример ответа:**
```json
{
    "success": true,
    "data": [...],
    "count": 3,
    "query": "python"
}
```

### 13. Курсы по уровню

**GET** `/courses/level/{min_level}/`

**Описание:** Получение курсов, доступных для указанного уровня (публичный endpoint)

**Параметры:**
- `min_level` (int) - Минимальный уровень пользователя

**Пример ответа:**
```json
{
    "success": true,
    "data": [...],
    "count": 5,
    "max_level": 3
}
```

### 14. Доступные курсы для пользователя

**GET** `/user/courses/available/`

**Описание:** Получение курсов, доступных для покупки пользователем (требует авторизации)

**Пример ответа:**
```json
{
    "success": true,
    "data": [...],
    "count": 8,
    "user_level": 5
}
```

## Коды ошибок

| Код | Описание |
|-----|----------|
| 200 | Успешный запрос |
| 201 | Ресурс успешно создан |
| 400 | Неверный запрос (ошибки валидации) |
| 401 | Не авторизован |
| 403 | Доступ запрещен |
| 404 | Ресурс не найден |
| 500 | Внутренняя ошибка сервера |

## Примеры использования

### Получение списка курсов с фильтрацией

```javascript
// Получить все курсы
fetch('/api/cours/courses/')
  .then(response => response.json())
  .then(data => console.log(data));

// Поиск курсов
fetch('/api/cours/courses/search/?q=python')
  .then(response => response.json())
  .then(data => console.log(data));
```

### Покупка курса

```javascript
fetch('/api/cours/courses/purchase/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Token your_token_here'
  },
  body: JSON.stringify({
    course_id: 1
  })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('Курс успешно куплен!');
  } else {
    console.error('Ошибка:', data.error);
  }
});
```

### Завершение урока

```javascript
fetch('/api/cours/lessons/complete/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Token your_token_here'
  },
  body: JSON.stringify({
    lesson_id: 1
  })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log(`Урок завершен! Получено ${data.earned_points} баллов`);
  }
});
```

## Особенности реализации

### Система баллов
- За завершение урока пользователь получает баллы (`reward_points`)
- За завершение всего курса начисляются дополнительные бонусные баллы
- Баллы добавляются к общему балансу пользователя (`coins`)

### Проверка доступности курсов
- Курсы имеют минимальный уровень (`min_level`)
- Пользователь может покупать только курсы, соответствующие его уровню
- Система автоматически фильтрует доступные курсы

### Прогресс по курсам
- Отслеживается количество завершенных уроков
- Рассчитывается процент прогресса
- Курс считается завершенным при прохождении всех уроков

### Поддержка Markdown
- Описания курсов и содержимое уроков поддерживают Markdown
- В админке Django настроены специальные виджеты для удобного редактирования
- Фронтенд должен рендерить Markdown в HTML

## Интеграция с фронтендом

Для интеграции с фронтендом рекомендуется:

1. Использовать библиотеку для рендеринга Markdown (например, `marked` для JavaScript)
2. Кэшировать данные курсов для улучшения производительности
3. Реализовать пагинацию для больших списков курсов
4. Добавить индикаторы загрузки для асинхронных операций
5. Обрабатывать все возможные ошибки API

## Безопасность

- Все endpoints, требующие авторизации, защищены декоратором `@token_required`
- Проверяется принадлежность пользователя к курсу перед выполнением операций
- Валидируются все входные данные через сериализаторы Django REST Framework
- Предотвращается повторное завершение уроков
- Проверяется достаточность средств перед покупкой курсов
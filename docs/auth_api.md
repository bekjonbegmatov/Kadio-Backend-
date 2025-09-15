# Kadio Authentication API Documentation

## Обзор

API для аутентификации и управления пользователями в системе Kadio. Предоставляет endpoints для регистрации, входа, управления профилем и загрузки аватаров.

## Базовый URL

```
/api/auth/
```

## Формат ответов

Все ответы возвращаются в формате JSON со следующей структурой:

### Успешный ответ
```json
{
    "success": true,
    "data": {...},
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

### 1. Регистрация пользователя

**POST** `/register/`

**Описание:** Регистрация нового пользователя в системе

**Тело запроса:**
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password123",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Пример успешного ответа:**
```json
{
    "success": true,
    "data": {
        "user": {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "level": 1,
            "coins": 100,
            "diamonds": 5,
            "avatar": null,
            "date_joined": "2024-01-15T10:30:00Z"
        },
        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    },
    "message": "Пользователь успешно зарегистрирован"
}
```

**Пример ответа с ошибкой:**
```json
{
    "success": false,
    "errors": {
        "username": ["Пользователь с таким именем уже существует"],
        "email": ["Пользователь с таким email уже существует"]
    }
}
```

### 2. Вход в систему

**POST** `/login/`

**Описание:** Аутентификация пользователя и получение токена доступа

**Тело запроса:**
```json
{
    "username": "john_doe",
    "password": "secure_password123"
}
```

**Пример успешного ответа:**
```json
{
    "success": true,
    "data": {
        "user": {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "level": 3,
            "coins": 450,
            "diamonds": 25,
            "avatar": "http://example.com/media/avatars/john_avatar.jpg",
            "date_joined": "2024-01-15T10:30:00Z",
            "last_login": "2024-01-20T14:15:00Z"
        },
        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    },
    "message": "Успешный вход в систему"
}
```

**Пример ответа с ошибкой:**
```json
{
    "success": false,
    "error": "Неверное имя пользователя или пароль"
}
```

### 3. Получение всех пользователей

**GET** `/users/all/`

**Описание:** Получение списка всех пользователей (публичный endpoint)

**Пример ответа:**
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "username": "john_doe",
            "first_name": "John",
            "last_name": "Doe",
            "level": 3,
            "avatar": "http://example.com/media/avatars/john_avatar.jpg",
            "date_joined": "2024-01-15T10:30:00Z"
        },
        {
            "id": 2,
            "username": "jane_smith",
            "first_name": "Jane",
            "last_name": "Smith",
            "level": 5,
            "avatar": "http://example.com/media/avatars/jane_avatar.jpg",
            "date_joined": "2024-01-10T08:20:00Z"
        }
    ],
    "count": 2
}
```

### 4. Получение профиля пользователя

**GET** `/profile/`

**Описание:** Получение профиля текущего авторизованного пользователя (требует токен)

**Заголовки:**
```
Authorization: Token <your_token_here>
```

**Пример ответа:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "level": 3,
        "coins": 450,
        "diamonds": 25,
        "avatar": "http://example.com/media/avatars/john_avatar.jpg",
        "date_joined": "2024-01-15T10:30:00Z",
        "last_login": "2024-01-20T14:15:00Z",
        "is_active": true,
        "is_staff": false
    }
}
```

### 5. Обновление профиля пользователя

**PUT** `/profile/update/`

**Описание:** Обновление данных профиля пользователя (требует токен)

**Заголовки:**
```
Authorization: Token <your_token_here>
Content-Type: application/json
```

**Тело запроса:**
```json
{
    "first_name": "John Updated",
    "last_name": "Doe Updated",
    "email": "john.updated@example.com"
}
```

**Пример успешного ответа:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "username": "john_doe",
        "email": "john.updated@example.com",
        "first_name": "John Updated",
        "last_name": "Doe Updated",
        "level": 3,
        "coins": 450,
        "diamonds": 25,
        "avatar": "http://example.com/media/avatars/john_avatar.jpg",
        "date_joined": "2024-01-15T10:30:00Z",
        "last_login": "2024-01-20T14:15:00Z"
    },
    "message": "Профиль успешно обновлен"
}
```

### 6. Загрузка аватара

**POST** `/profile/upload-avatar/`

**Описание:** Загрузка аватара пользователя (требует токен)

**Заголовки:**
```
Authorization: Token <your_token_here>
Content-Type: multipart/form-data
```

**Тело запроса (form-data):**
```
avatar: [файл изображения]
```

**Пример успешного ответа:**
```json
{
    "success": true,
    "data": {
        "avatar_url": "http://example.com/media/avatars/john_new_avatar.jpg"
    },
    "message": "Аватар успешно загружен"
}
```

**Пример ответа с ошибкой:**
```json
{
    "success": false,
    "error": "Неподдерживаемый формат файла. Разрешены: JPG, PNG, GIF"
}
```

## Аутентификация

### Система токенов

После успешной регистрации или входа в систему, пользователь получает токен доступа. Этот токен должен быть включен в заголовок `Authorization` для всех защищенных endpoints:

```
Authorization: Token <your_token_here>
```

### Защищенные endpoints

Следующие endpoints требуют аутентификации:
- `GET /profile/` - получение профиля
- `PUT /profile/update/` - обновление профиля
- `POST /profile/upload-avatar/` - загрузка аватара

### Публичные endpoints

Следующие endpoints доступны без аутентификации:
- `POST /register/` - регистрация
- `POST /login/` - вход в систему
- `GET /users/all/` - список всех пользователей

## Коды ошибок

| Код | Описание |
|-----|----------|
| 200 | Успешный запрос |
| 201 | Ресурс успешно создан |
| 400 | Неверный запрос (ошибки валидации) |
| 401 | Не авторизован (неверный или отсутствующий токен) |
| 403 | Доступ запрещен |
| 404 | Ресурс не найден |
| 409 | Конфликт (например, пользователь уже существует) |
| 500 | Внутренняя ошибка сервера |

## Валидация данных

### Регистрация пользователя

**Обязательные поля:**
- `username` - имя пользователя (3-150 символов, уникальное)
- `email` - email адрес (валидный email, уникальный)
- `password` - пароль (минимум 8 символов)

**Необязательные поля:**
- `first_name` - имя (максимум 150 символов)
- `last_name` - фамилия (максимум 150 символов)

### Обновление профиля

**Доступные для изменения поля:**
- `first_name` - имя
- `last_name` - фамилия
- `email` - email адрес (должен быть уникальным)

**Примечание:** `username` нельзя изменить после регистрации.

### Загрузка аватара

**Требования к файлу:**
- Поддерживаемые форматы: JPG, JPEG, PNG, GIF
- Максимальный размер: 5 МБ
- Рекомендуемые размеры: 200x200 пикселей (квадратное изображение)

## Примеры использования

### Регистрация и вход

```javascript
// Регистрация нового пользователя
fetch('/api/auth/register/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'john_doe',
    email: 'john@example.com',
    password: 'secure_password123',
    first_name: 'John',
    last_name: 'Doe'
  })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    // Сохранить токен для дальнейшего использования
    localStorage.setItem('authToken', data.data.token);
    console.log('Регистрация успешна!');
  } else {
    console.error('Ошибки регистрации:', data.errors);
  }
});

// Вход в систему
fetch('/api/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'john_doe',
    password: 'secure_password123'
  })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    localStorage.setItem('authToken', data.data.token);
    console.log('Вход выполнен успешно!');
  } else {
    console.error('Ошибка входа:', data.error);
  }
});
```

### Работа с профилем

```javascript
// Получение профиля пользователя
fetch('/api/auth/profile/', {
  headers: {
    'Authorization': `Token ${localStorage.getItem('authToken')}`
  }
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('Профиль пользователя:', data.data);
  }
});

// Обновление профиля
fetch('/api/auth/profile/update/', {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Token ${localStorage.getItem('authToken')}`
  },
  body: JSON.stringify({
    first_name: 'John Updated',
    last_name: 'Doe Updated'
  })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('Профиль обновлен!');
  }
});
```

### Загрузка аватара

```javascript
// Загрузка аватара
const formData = new FormData();
const fileInput = document.getElementById('avatar-input');
formData.append('avatar', fileInput.files[0]);

fetch('/api/auth/profile/upload-avatar/', {
  method: 'POST',
  headers: {
    'Authorization': `Token ${localStorage.getItem('authToken')}`
  },
  body: formData
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('Аватар загружен:', data.data.avatar_url);
    // Обновить изображение аватара на странице
    document.getElementById('user-avatar').src = data.data.avatar_url;
  } else {
    console.error('Ошибка загрузки:', data.error);
  }
});
```

## Система уровней и валюты

### Уровни пользователей
- Новые пользователи начинают с уровня 1
- Уровень повышается за выполнение различных активностей
- Уровень влияет на доступность курсов и функций

### Внутренняя валюта
- **Coins (монеты)** - основная валюта для покупки курсов
- **Diamonds (алмазы)** - премиум валюта для особых покупок
- Новые пользователи получают стартовый бонус: 100 монет и 5 алмазов

## Безопасность

### Защита паролей
- Пароли хешируются с использованием Django's PBKDF2
- Минимальная длина пароля: 8 символов
- Рекомендуется использовать сложные пароли

### Токены доступа
- Токены генерируются с использованием JWT
- Токены не имеют срока истечения (stateless)
- Для выхода из системы достаточно удалить токен на клиенте

### Загрузка файлов
- Проверка типа файла по расширению и MIME-типу
- Ограничение размера файла
- Файлы сохраняются в безопасной директории

## Интеграция с другими модулями

API аутентификации интегрируется с:
- **Courses API** - проверка уровня пользователя для доступа к курсам
- **Chat API** - идентификация пользователей в чате
- **Activities API** - отслеживание активности пользователей
- **Gamification** - система уровней и достижений

## Миграции и обновления

При обновлении API учитывайте:
- Обратную совместимость токенов
- Миграцию пользовательских данных
- Обновление клиентских приложений
- Тестирование всех endpoints после изменений
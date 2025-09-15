# Kadio-Backend-

Kadio — это приложение, которое помогает студентам не бросать онлайн-курсы и доходить до конца. Мы превращаем учёбу в увлекательное путешествие: привычки, награды, прогресс и рекомендации делают процесс интересным и мотивирующим.

## Установка и запуск проекта

### 1. Клонирование репозитория

```bash
git clone https://github.com/bekjonbegmatov/Kadio-Backend-.git
cd Kadio-Backend-
```

### 2. Создание и активация виртуального окружения

```bash
# Создание виртуального окружения
python -m venv venv

# Активация виртуального окружения
# На Windows:
venv\Scripts\activate

# На macOS/Linux:
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r moduls.txt
```

### 4. Создание и применение миграций

```bash
# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate
```

### 5. Создание суперпользователя

Для доступа к административной панели необходимо создать суперпользователя:

```bash
python manage.py createsuperuser
```

### 6. Сбор статических файлов

```bash
python manage.py collectstatic --noinput
```

### 7. Запуск сервера

Запуск сервера осуществляется с помощью Uvicorn:

```bash
# Локальный запуск
uvicorn server.asgi:application

# Запуск с доступом для всех устройств в сети
uvicorn server.asgi:application --host 0.0.0.0 --port 8000

# Или с конкретным IP-адресом
uvicorn server.asgi:application --host <ваш_ip> --port 8000
```

### Доступ к приложению

- **API**: http://localhost:8000/api/
- **Административная панель**: http://localhost:8000/admin/

При запуске с параметром `--host 0.0.0.0` или конкретным IP, замените `localhost` на соответствующий адрес.

Создано с ❤️ Bekjon Begmatov для хакатона "ИТ Старт"
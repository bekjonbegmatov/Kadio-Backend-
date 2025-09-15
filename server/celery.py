import os
from celery import Celery

# Устанавливаем переменную окружения для Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

# Создаем экземпляр Celery
app = Celery('server')

# Загружаем конфигурацию из Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически обнаруживаем задачи в приложениях Django
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
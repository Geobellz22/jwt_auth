import os
from celery import Celery
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")  # Defaults to local Redis

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jwt_auth.settings")

app = Celery("jwt_auth")
app.conf.broker_url = REDIS_URL  # Message broker (Redis URL)
app.conf.result_backend = REDIS_URL  # Store Celery results in Redis
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


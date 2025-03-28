import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jwt_auth.settings')  # Replace 'your_project' with your actual project name

app = Celery('jwt_auth')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all Django apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

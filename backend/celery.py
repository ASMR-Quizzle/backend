import os
from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# app = Celery("quizzle")
app = Celery(
    "backend",
    broker="redis://redis",
    # include=[
    #     "backend.tasks",
    # ],
    backend="redis://redis",
)
# app.conf.update(settings.CELERY)
app.autodiscover_tasks()

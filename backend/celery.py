# import os
# from celery import Celery
# from django.conf import settings

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# # app = Celery("quizzle")
# app = Celery(
#     "backend",
#     broker="redis://redis",
#     # include=[
#     #     "backend.tasks",
#     # ],
#     backend="redis://redis",
# )
# # app.conf.update(settings.CELERY)
# app.autodiscover_tasks()

from __future__ import absolute_import
import os
import queue
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
app = Celery("backend", broker="redis://redis:6379/0", backend="redis://redis:6379/0")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True, queue="backend")
def debug_task(self):
    print(f"Request: {self.request!r}")


if __name__ == "__main__":
    app.start()

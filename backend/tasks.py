import os
from celery.utils.log import get_task_logger
from time import sleep
import requests
import sys
from .celery import app
from django.conf import settings
from celery import shared_task

sys.stdout.flush()

logger = get_task_logger(__name__)


@shared_task
def example_task():
    print("ereeeee")
    sleep(5)
    logger.info(f"GET returned status_code ")
    return 0

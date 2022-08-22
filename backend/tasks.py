from time import sleep
from celery import shared_task


@shared_task
def example_task(pk):
    print("ereeeee", pk)
    sleep(50)
    return 5

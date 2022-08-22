from rest_framework import generics
from rest_framework.response import Response

from .serializers import PingSerializer
from .tasks import example_task
from celery.result import AsyncResult


class Ping(generics.GenericAPIView):
    serializer_class = PingSerializer

    def get(self, request, *args, **kwargs):
        return Response({"data": "pong"})


class ExampleTaskAPI(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        task = example_task.delay(1)
        print(task.status)
        return Response(str(task), status=201)


class RetrieveTask(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        task = AsyncResult(request.GET.get("task_id"))
        print(task.status)
        return Response(
            data={"status": task.status, "info": task.info, "result": task.result},
            status=201,
        )

from rest_framework import generics
from rest_framework.response import Response

from .serializers import PingSerializer


class Ping(generics.GenericAPIView):
    serializer_class = PingSerializer

    def get(self, request, *args, **kwargs):
        return Response({"data": "pong"})

from rest_framework import generics
from rest_framework.response import Response


class Ping(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        return Response({"data": "pong"})

from rest_framework import viewsets, permissions
from rest_framework.response import Response
from yaml import serialize
from question.models import Question
from question.serializers import QuestionSerializer


# Create your views here.

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        user = request.user
        if user.is_setter:
            queryset = self.queryset.filter(setter=user)
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data)
        elif user.is_reviewer:
            queryset = self.queryset.exclude(setter=user)
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data)

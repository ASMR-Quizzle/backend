from user.utils import get_tokens_for_user
from rest_framework.response import Response
from institute.serializers import CreateInstituteProfileSerializer
from rest_framework import generics

# Create your views here.
class InstituteRegistrationAPI(generics.GenericAPIView):
    serializer_class = CreateInstituteProfileSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_tokens_for_user(user)
        return Response({"data": {"token": token}})

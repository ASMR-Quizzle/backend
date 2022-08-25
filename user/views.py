from question.models import UserEligibilityTest
from .serializers import (
    CreateUserProfileSerializer,
    RewardsSerializer,
    UserEligibleTopicsSerializer,
    UserSerializer,
)
from rest_framework.decorators import action
from rest_framework import generics, viewsets
from rest_framework.response import Response
from .utils import get_tokens_for_user
from .models import Reward, AppUser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

# Create your views here.
class UserRegistrationAPI(generics.GenericAPIView):
    serializer_class = CreateUserProfileSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_tokens_for_user(user)
        return Response(token)


class RewardsAPI(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RewardsSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        appUser = user.appuser
        if appUser.is_reviewer == False and appUser.is_setter == False:
            return Response(
                status=403, data={"error": "user not a eligible for rewards"}
            )
        reward = appUser.reward
        if reward is None:
            return Response(
                status=404, data={"error": "No wallet associated with current user"}
            )
        return Response(
            {"data": {"address": reward.wallet_address, "points": reward.points}}
        )

    def post(self, request, *args, **kwargs):
        user = request.user
        appUser = user.appuser

        if appUser.is_reviewer == False and appUser.is_setter == False:
            return Response(
                status=406, data={"error": "user not a eligible for rewards"}
            )
        reward = appUser.reward
        if reward is not None:
            return Response(
                status=409,
                data={"error": "user already has a wallet associated with the account"},
            )
        wallet_address = request.data["wallet_address"]
        reward = Reward(wallet_address=wallet_address)
        appUser.reward = reward
        reward.save()
        appUser.save()
        return Response(
            {
                "data": {"address": reward.wallet_address, "points": reward.points},
                "message": "Wallet Connected to Quizzle successfully",
            }
        )


class UserEligibleTopicsAPI(generics.GenericAPIView):
    serializer_class = UserEligibleTopicsSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        if (
            request.user.appuser.is_setter == False
            and request.user.appuser.is_reviewer == False
        ):
            return Response(
                data={"error": "User is neither a setter nor a reviewer"}, status=400
            )
        topics = UserEligibilityTest.objects.filter(
            appuser=request.user.appuser, is_eligible=True
        ).values()
        return Response(data={"data": topics})

class UserAPI(viewsets.ModelViewSet):
    queryset = AppUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsAuthenticatedOrReadOnly, )

    @action(detail=False, methods=['get'], url_name='profile', url_path='profile')
    def profile(self, request, *args, **kwargs):
        try:
            user = request.user
            app_user = self.queryset.get(user=user)
            serializer = self.serializer_class(app_user)
            return Response(data=serializer.data, status=200)
        except:
            return Response(data={'message': 'Server Error occured'}, status=500)

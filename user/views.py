from os import stat
from .serializers import (
    CreateUserProfileSerializer,
    RewardsSerializer,
)
from rest_framework import generics
from rest_framework.response import Response
from .utils import get_tokens_for_user
from .models import Reward
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class UserRegistrationAPI(generics.GenericAPIView):
    serializer_class = CreateUserProfileSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_tokens_for_user(user)
        return Response({"data": {"token": token}})


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

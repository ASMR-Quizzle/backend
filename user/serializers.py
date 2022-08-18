from rest_framework import serializers
from django.contrib.auth.models import User
from .models import AppUser


class CreateUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser

        fields = (
            "email",
            "username",
            "is_setter",
            "is_reviewer",
            "is_active",
            "password",
            "phone_number",
        )
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
        )
        user.set_password(validated_data["password"])
        user.save()
        user_profile = AppUser(
            user=user,
            username=validated_data["username"],
            email=validated_data["email"],
            is_setter=validated_data["is_setter"],
            is_reviewer=validated_data["is_reviewer"],
            phone_number=validated_data["phone_number"],
            is_active=False,
        )
        user_profile.save()
        return user


class RewardsSerializer(serializers.Serializer):
    wallet_address = serializers.CharField()

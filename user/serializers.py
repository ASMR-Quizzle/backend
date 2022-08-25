from rest_framework import serializers
from django.contrib.auth.models import User
from .models import AppUser


class CreateUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser

        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        )
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        user_profile = AppUser(
            user=user,
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            is_active=True,
        )
        user_profile.save()
        return user


class RewardsSerializer(serializers.Serializer):
    wallet_address = serializers.CharField()


class UserEligibleTopicsSerializer(serializers.Serializer):
    pass

class UserSerializer(serializers.ModelSerializer):
    user = CreateUserProfileSerializer(read_only=True)

    class Meta:
        model = AppUser
        fields = '__all__'

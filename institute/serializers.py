from rest_framework import serializers
from django.contrib.auth.models import User
from institute.models import Institute


class CreateInstituteProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institute

        fields = ("email", "username", "password", "name")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
        )
        user.set_password(validated_data["password"])
        user.save()
        institute_profile = Institute(
            user=user,
            username=validated_data["username"],
            email=validated_data["email"],
            name=validated_data["name"],
        )
        institute_profile.save()
        return institute_profile

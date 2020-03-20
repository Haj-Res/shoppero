from django.contrib.auth import get_user_model
from rest_framework import serializers

from account.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name')


class ChangePasswordSerializer(serializers.Serializer):
    model = get_user_model()

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('avatar',)

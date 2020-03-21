import logging

from django.contrib.auth import get_user_model
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from account.models import Profile
from settings.serializers import ProfileSerializer, ChangePasswordSerializer, \
    AvatarSerializer

logger = logging.getLogger('shoppero')


class SettingsView(TemplateView):
    template_name = 'settings/settings.html'


class ProfileViewSet(ViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer

    def get_object(self):
        """
        Get this endpoint's instance object
        :return: authenticated user's profile
        """
        return self.request.user.profile

    def patch(self, request):
        """
        Endpoint for updating basic profile information
        :param request: DRF request
        :return: DRF Response object containing serialized data or
        submission errors and status
        """
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class PasswordViewSet(ViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer
    model = get_user_model()

    def get_object(self):
        """
        Get this endpoint's instance object
        :return: return authenticated user
        """
        return self.request.user

    def update(self, request, *args, **kwargs):
        """
        Endpoint for changing the password of the logged in user.
        :param request: DRF request object
        :return: Response with either errors or status 200
        """
        user = self.get_object()
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            if not user.check_password(
                    serializer.validated_data['old_password']):
                return Response({"old_password": ["Wrong password."]},
                                status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class AvatarViewSet(ViewSet):
    serializer_class = AvatarSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        """
        Method to get the instance of the objects for the endpoint
        :return: authenticated user's profile object
        """
        return self.request.user.profile

    def post(self, request, *args, **kwargs):
        """
        Endpoint for changing the user's avatar image
        :param request: DRF request object containing the image
        :return: DRF Response object with new image url or submission errors
        and  http status
        """
        logger.info('User %d changing avatar %s', request.user.id,
                    request.data)
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            logger.error(serializer.errors)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """
        Endpoint for deleting the user's avatar image and setting it back
        to the default avatar image
        :param request: DRF request object
        :return: Response with default avatar URL and http status
        """
        logger.info('User %d deleting avatar')
        instance = self.get_object()
        if instance.avatar != Profile.DEFAULT_AVATAR:
            instance.avatar.delete(save=True)
            instance.avatar = Profile.DEFAULT_AVATAR
            instance.save()
        return Response({'avatar': instance.avatar.url},
                        status=status.HTTP_200_OK)

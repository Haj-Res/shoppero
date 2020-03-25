import logging

from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from account.forms import TwoFactorForm
from account.models import Profile
from account.tokens import account_activation_token
from core import string_constants
from settings.serializers import ProfileSerializer, ChangePasswordSerializer, \
    AvatarSerializer, DefaultShareLevelSerializer

logger = logging.getLogger('shoppero')


class SettingsView(TemplateView):
    template_name = 'settings/settings.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(SettingsView, self).dispatch(request, *args, **kwargs)


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
            login(request, user)
            return Response({'message': 'Password changed'},
                            status=status.HTTP_200_OK)
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
            logger.debug(serializer.errors)
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


class TwoFactorViewSet(ViewSet):
    permission_classes = (IsAuthenticated,)
    form_class = TwoFactorForm

    def get_object(self):
        return self.request.user

    def get(self, request):
        user = self.get_object()
        user.security.generate_token()
        token_2 = user.security.token_2
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        utokenb64 = urlsafe_base64_encode(force_bytes(token_2))
        url = reverse_lazy('two-factor-toggle', args=[uidb64, utokenb64])
        context = {'url': url}
        return Response(context, status=status.HTTP_200_OK)

    def post(self, request, uidb64=None, utokenb64=None):
        logger.info('User %d toggling 2FA')
        logger.debug(request.data)
        form = self.form_class(data=request.data)
        if form.is_valid():
            user = self.get_object()
            pk = force_str(urlsafe_base64_decode(uidb64))
            if pk != str(user.pk):
                return Response({'message': 'Invalid uidb64'},
                                status=status.HTTP_404_NOT_FOUND)
            token = form.cleaned_data['token']
            token_2 = force_str(urlsafe_base64_decode(utokenb64))
            if user.security.is_token_valid(token, token_2):
                user.security.two_factor = not user.security.two_factor
                if user.security.two_factor:
                    message = 'Two Factor Authentication enabled'
                else:
                    message = 'Two Factor Authentication disabled'
                user.security.reset_token_data()
                return Response({'message': message},
                                status=status.HTTP_200_OK)
            else:
                user.security.login_attempts += 1
                user.security.save()
                return Response({'message': 'Invalid authentication code'},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class DefaultShareLevelViewSet(ViewSet):
    """
    View for updating the logged in user's default shopping list share level.
    """
    serializer_class = DefaultShareLevelSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self) -> Profile:
        """
        Method that returns the authenticated user's profile object
        :return: Profile
        """
        return self.request.user.profile

    def patch(self, request):
        logger.info('User %d changing default share level')
        logger.debug(request.data)
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            logger.debug(serializer.errors)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class DeleteAccountViewSet(ViewSet):
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def delete_step_one(self, request):
        """View for sending the delete confirmation email to the user
        First step out of two for deleting an account"""
        user = self.get_object()
        logger.info('User %d requesting account delete email')
        domain = get_current_site(self.request).domain
        subject = str(string_constants.DELETE_ACCOUNT_SUBJECT)
        message = render_to_string('mail/delete_account.html', {
            'domain': domain,
            'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        user.email_user(subject, message)
        logger.info('Sent email for deleting account')
        return Response(
            {'message': str(string_constants.DELETE_ACCOUNT_EMAIL_SENT)},
            status=status.HTTP_200_OK
        )

    def delete_step_two(self, request, uidb64, token):
        """View for confirming account delete. Second step out of two.
        View logs out user for successful and failed delete attempt"""
        user = self.get_object()
        logger.info('Used %d confirming account delete: uidb64 %s - token: %s',
                    user.pk, uidb64, token)
        pk = force_str(urlsafe_base64_decode(uidb64))
        if str(user.pk) == pk \
                and account_activation_token.check_token(user, token):
            user.soft_delete()
            user.save()
            messages.success(request,
                             'Your account was successfully deleted.')
            logger.info('User %d successfully deleted account', user.pk)
        else:
            logger.info('Invalid confirmation link')
            messages.error(request,
                           'The link for account deletion is invalid.')
        logout(request)
        return redirect('auth_login')

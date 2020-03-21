import logging
import os
import secrets
import uuid
from datetime import timedelta
from typing import Optional, List

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from account.managers import UserManager
from core.models import SoftDeleteModel
from utils.send_mail import send_mail

logger = logging.getLogger('shoppero')


def avatar_file_path(instance, filename):
    """Generate file path for new recipe image"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('avatars/', filename)


class User(AbstractBaseUser, SoftDeleteModel, PermissionsMixin):
    email = models.EmailField(unique=True, null=False, blank=False)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this site.')
    )
    is_active = models.BooleanField(
        _('active'),
        default=False,
        help_text=_('Designates whether this user should '
                    'be treated as active.')
    )

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

    objects = UserManager()

    def __str__(self) -> str:
        return str(self.email)

    def email_user(self, subject: str, message: str, from_email: str = None,
                   cc_list: Optional[List[str]] = None, **kwargs) -> None:
        """Send an email to this user."""
        send_mail(subject, message, [self.email], sender=from_email,
                  cc_list=cc_list, **kwargs)


class Profile(models.Model):
    DEFAULT_AVATAR = 'default-profile-image.png'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(default=DEFAULT_AVATAR,
                               upload_to=avatar_file_path)

    def __str__(self):
        return self.user.email


class Security(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    two_factor = models.BooleanField(default=False)
    token = models.CharField(max_length=12, blank=True)
    token_2 = models.CharField(max_length=12, blank=True)
    valid_until = models.DateTimeField(blank=True, null=True)
    login_attempts = models.IntegerField(default=0)

    def __str__(self):
        return str(self.user) + '(' + str(self.two_factor) + ')'

    def generate_token(self,
                       length: int = settings.TWO_FACTOR_TOKEN_LENGTH,
                       valid_minutes: int =
                       settings.TWO_FACTOR_TOKEN_VALID_MIN) -> None:
        """
        Generate a token for two factor login authentication. Save it in DB
        and generate a valid until date for the token. Uses default values
        from the global project settings file.
        :param length: length of the token
        :param valid_minutes: how many minutes the token is valid
        """
        token = ''
        token_2 = ''
        for i in range(length):
            digit = secrets.randbelow(10)
            token += str(digit)
            digit = secrets.randbelow(10)
            token_2 += str(digit)
        self.token = token
        self.token_2 = token_2
        self.valid_until = timezone.now() + timedelta(minutes=valid_minutes)
        self.save()
        self.send_token_email()

    def login_successful(self):
        """Reset token data used to confirm login"""
        self.token = ''
        self.token_2 = ''
        self.login_attempts = 0
        self.valid_until = None
        self.save()

    def send_token_email(self):
        """Method for sending authentication code to user email"""
        logger.info('Sending email for two factor authentication')
        subject = _('Login authentication code')
        message = render_to_string('mail/two_factor_email.html', {
            'token': self.token
        })
        self.user.email_user(subject, message)


@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    """
    Signal receiver function for creating user profile alongside the user
    object.
    :param sender: User class
    :param instance: instance of the user
    :param created: boolean value whether the user was created or not (updated)
    :param kwargs: other arguments
    :return: None
    """
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


@receiver(post_save, sender=User)
def create_user_security_signal(sender, instance, created, **kwargs):
    if created:
        Security.objects.create(user=instance)
        instance.security.save()

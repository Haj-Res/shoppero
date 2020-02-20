from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import ugettext_lazy as _

from account.managers import UserManager
from core.mixins import SoftDeleteMixin


class User(AbstractBaseUser, SoftDeleteMixin, PermissionsMixin):
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

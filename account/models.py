from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from account.managers import UserManager
from core.mixins import SoftDeleteMixin
from utils.send_mail import send_mail


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

    def email_user(self, subject, message, from_email=None, cc_list=None,
                   **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, [self.email], sender=from_email,
                  cc_list=cc_list, **kwargs)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.email


@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    """
    Customized user manager for managing custom user model that uses
    an email instead of a username for login purposes
    """

    def _create_user(self, email: str, password: str, **kwargs):
        """
        Create and save a user with given email and password
        :param email: user's email, must be in a valid form
        :param password: user's password
        :param kwargs: additional user parameter
        :return: User
        """
        if not email:
            raise ValueError(_('User must have an email'))
        if not password:
            raise ValueError(_('User must have a password'))
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_active', True)

        if kwargs.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if kwargs.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        return self._create_user(email, password, **kwargs)

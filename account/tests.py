from django.contrib.auth import get_user_model
from django.test import TestCase


class TestUserCreation(TestCase):
    def setUp(self) -> None:
        self.valid_email = 'test@user.com'
        self.valid_pass = 'testpass'
        self.invalid_email = None
        self.invalid_pass = None

    def test_create_user(self):
        """Test user creation"""
        user = get_user_model().objects.create_user(
            email=self.valid_email,
            password=self.valid_pass
        )
        self.assertIsNotNone(user.id)

    def test_create_user_fail(self):
        """Test user creation fails without email"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=self.invalid_email,
                password=self.valid_pass
            )
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=self.valid_email,
                password=self.invalid_pass
            )

    def test_create_super_user(self):
        """Test super user creation"""
        user = get_user_model().objects.create_superuser(
            email=self.valid_email,
            password=self.valid_pass
        )
        self.assertIsNotNone(user.id)

    def test_create_super_user_fail(self):
        """Test super user creation fail without email, password,
        is_stuff=False or is_superuser=False"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_superuser(
                email=self.invalid_email,
                password=self.valid_pass
            )
        with self.assertRaises(ValueError):
            get_user_model().objects.create_superuser(
                email=self.valid_email,
                password=self.invalid_pass
            )
        with self.assertRaises(ValueError):
            get_user_model().objects.create_superuser(
                email=self.valid_email,
                password=self.valid_pass,
                is_staff=False
            )
        with self.assertRaises(ValueError):
            get_user_model().objects.create_superuser(
                email=self.valid_email,
                password=self.valid_pass,
                is_superuser=False
            )

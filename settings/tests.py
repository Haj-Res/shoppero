import io

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APIClient

from account.models import Profile
from account.tokens import account_activation_token

BASIC_INFORMATION_URL = reverse('profile')
PASSWORD_URL = reverse('change-password')
AVATAR_CHANGE_URL = reverse('change-avatar')
SHARE_LEVEL_URL = reverse('share-level')
DELETE_ACCOUNT_URL = reverse('delete-account-s1')


def sample_user(email='user@shoppero.com', password='pass'):
    """Helper function for creating sample user"""
    return get_user_model().objects.create_user(email, password)


def generate_photo_file():
    """Helper function for generating image for testing"""
    file = io.BytesIO()
    image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
    image.save(file, 'png')
    file.name = 'test.png'
    file.seek(0)
    return file


class TestUserSettingsPublic(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_change_basic_information_fail(self):
        """Test that the api for changing basic user data is not public"""
        payload = {'first_name': ''}
        res = self.client.patch(BASIC_INFORMATION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_change_password_fail(self):
        """Test that the api for changing user password is not public"""
        payload = {'password': ''}
        res = self.client.post(PASSWORD_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_change_image_fail(self):
        """Test that the api for changing user avatar is not public"""
        avatar = generate_photo_file()
        payload = {'avatar': avatar}
        res = self.client.post(AVATAR_CHANGE_URL, payload, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_change_default_share_level_fail(self):
        """Test that the api for changing user default share level
        is not public"""
        payload = {'share_level': Profile.COMPLETE_ACCESS}
        res = self.client.patch(SHARE_LEVEL_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_account_send_mail_fail(self):
        """Test that the api for sending delete confirmation mail
        is not public"""
        res = self.client.get(DELETE_ACCOUNT_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_account_final_fail(self):
        """Test that the api for deleting the account is not public"""
        delete_account_confirm_url = reverse('delete-account-s2',
                                             args=['any_id', 'any_token'])
        res = self.client.get(delete_account_confirm_url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class TestUserSettingsPrivate(TestCase):
    def setUp(self) -> None:
        self.user = sample_user()
        self.user.refresh_from_db()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_change_basic_information_success(self):
        """Test user change basic information api success"""
        payload = {
            'first_name': 'John',
            'last_name': 'Doe'
        }
        res = self.client.patch(BASIC_INFORMATION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.first_name, payload['first_name'])
        self.assertEqual(self.user.profile.last_name, payload['last_name'])

    def test_change_password_success(self):
        """Test that user can change password successfully"""
        payload = {
            'old_password': 'pass',
            'new_password': 'pass2'
        }
        res = self.client.post(PASSWORD_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        res = self.user.check_password(payload['new_password'])
        self.assertTrue(res)

    def test_change_password_fail(self):
        """Test that user can't change password with invalid old password"""
        invalid_payload = {
            'old_password': 'invalid_pass',
            'new_password': ''
        }
        res = self.client.post(PASSWORD_URL, invalid_payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_avatar_success(self):
        """Test that user can change their avatar image"""
        avatar = generate_photo_file()
        payload = {'avatar': avatar}
        res = self.client.post(AVATAR_CHANGE_URL, payload, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_avatar_success(self):
        """Test that user can delete their avatar image and
        reset it to the default image"""
        avatar = generate_photo_file()
        payload = {'avatar': avatar}
        res = self.client.post(AVATAR_CHANGE_URL, payload, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(Profile.DEFAULT_AVATAR, res.data['avatar'])
        res = self.client.delete(AVATAR_CHANGE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(Profile.DEFAULT_AVATAR, res.data['avatar'])

    def test_change_share_level_success(self):
        """Test that user can change their default share level successfully"""
        self.assertEqual(self.user.profile.share_level, Profile.READ_ACCESS)
        payload = {'share_level': Profile.COMPLETE_ACCESS}
        res = self.client.patch(SHARE_LEVEL_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.profile.share_level,
                         Profile.COMPLETE_ACCESS)

    def test_change_share_level_invalid_choice(self):
        """Test that the user can no change default share level to
        an invalid choice"""
        payload = {'share_level': 'invalid_string'}
        res = self.client.patch(SHARE_LEVEL_URL, payload)
        self.user.profile.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.user.profile.share_level, Profile.READ_ACCESS)

    def test_delete_account_send_email_success(self):
        """Test that the user can get the delete account
        confirmation email"""
        res = self.client.get(DELETE_ACCOUNT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_account_confirm_success(self):
        """Test that the user can delete their account"""
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_activation_token.make_token(self.user)
        delete_account_confirm_url = reverse('delete-account-s2',
                                             args=[uidb64, token])
        res = self.client.get(delete_account_confirm_url)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.deleted)

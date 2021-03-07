from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status


class TokenTestCase(TestCase):
    def setUp(self):
        self.user_name = 'test_name'
        self.user_password = 'test_password'
        self.user = User.objects.create_user(username=self.user_name,
                                             password=self.user_password)

    def test_valid_user(self):
        url = '/generate_token/'
        data = {
            "username": self.user_name,
            "password": self.user_password
        }
        response = self.client.post(url, data=data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_invalid_user(self):
        url = '/generate_token/'
        data = {
            "username": 'some_name',
            "password": 'some_password'
        }
        response = self.client.post(url, data=data, content_type='application/json')
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

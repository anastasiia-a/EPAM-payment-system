import json

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from wallets.models import Wallet


class WalletCRUDTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Test user', password='Test password')
        self.token = Token.objects.create(user=self.user)
        self.wallet_1 = Wallet.objects.create(name='wallet_1', client_firstname='firstname_1',
                                              client_surname='surname_1')
        self.wallet_2 = Wallet.objects.create(name='wallet_2', client_firstname='firstname_2',
                                              client_surname='surname_2')

    def test_read_without_token(self):
        response = self.client.get('/wallets/')
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_create_without_token(self):
        data = {
            "client_firstname": 'firstname_3',
            "client_surname": 'surname_3',
        }
        json_data = json.dumps(data)
        response = self.client.post('/wallets/', data=json_data,
                                    content_type='application/json')

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual(2, Wallet.objects.count())

    def test_update_without_token(self):
        old_surname = self.wallet_2.client_surname
        new_data = {
            "client_firstname": self.wallet_2.client_firstname,
            "client_surname": 'new surname',
        }
        url = '/wallets/' + str(self.wallet_2.id) + '/'
        response = self.client.post(url, data=json.dumps(new_data),
                                    content_type='application/json')

        self.wallet_2.refresh_from_db()
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual(old_surname, self.wallet_2.client_surname)

    def test_delete_without_token(self):
        url = '/wallets/' + str(self.wallet_1.id) + '/'
        response = self.client.delete(url, content_type='application/json')

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual(2, Wallet.objects.count())

    def test_read(self):
        response = self.client.get('/wallets/',
                                   HTTP_AUTHORIZATION='Token ' + str(self.token),
                                   content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_create(self):
        self.assertEqual(2, Wallet.objects.count())
        data = {
            "client_firstname": 'firstname_3',
            "client_surname": 'surname_3',
        }
        json_data = json.dumps(data)
        response = self.client.post('/wallets/', data=json_data,
                                    HTTP_AUTHORIZATION='Token ' + str(self.token),
                                    content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(3, Wallet.objects.count())

    def test_update(self):
        self.assertEqual('surname_1', self.wallet_1.client_surname)
        data = {
            "client_firstname": self.wallet_1.client_firstname,
            "client_surname": 'new_surname',
        }
        json_data = json.dumps(data)
        url = '/wallets/' + str(self.wallet_1.id) + '/'
        response = self.client.post(url, data=json_data,
                                    HTTP_AUTHORIZATION='Token ' + str(self.token),
                                    content_type='application/json')

        self.wallet_1.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('new_surname', self.wallet_1.client_surname)

    def test_delete(self):
        self.assertEqual(2, Wallet.objects.count())
        url = '/wallets/' + str(self.wallet_1.id) + '/'
        response = self.client.delete(url,
                                      HTTP_AUTHORIZATION='Token ' + str(self.token),
                                      content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, Wallet.objects.count())

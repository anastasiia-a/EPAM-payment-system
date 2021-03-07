from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from wallets.models import Wallet


class OperationsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')
        self.token = Token.objects.create(user=self.user)
        self.wallet1 = Wallet.objects.create(name='wallet 1',
                                             client_firstname='firstname 1',
                                             client_surname='surname 1',
                                             balance=Decimal("500.00"))
        self.wallet2 = Wallet.objects.create(name='wallet 2',
                                             client_firstname='firstname 2',
                                             client_surname='surname 2')

    def test_deposit_without_token(self):
        self.assertEqual(Decimal("500.00"), self.wallet1.balance)
        url = f"/wallets/{self.wallet1.id}/deposits/"
        data = {
            "amount": 2000
        }
        response = self.client.post(url, data=data, content_type='application/json')
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.wallet1.refresh_from_db()
        self.assertEqual(Decimal("500.00"), self.wallet1.balance)

    def test_withdrawal_without_token(self):
        self.assertEqual(Decimal("500.00"), self.wallet1.balance)
        self.assertEqual(Decimal("0.00"), self.wallet2.balance)
        url = f"/wallets/{self.wallet1.id}/withdrawals/{self.wallet2.id}/"
        data = {
            "amount": 1000
        }
        response = self.client.post(url, data=data, content_type='application/json')
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.wallet1.refresh_from_db()
        self.wallet2.refresh_from_db()
        self.assertEqual(Decimal("500.00"), self.wallet1.balance)
        self.assertEqual(Decimal("0.00"), self.wallet2.balance)

    def test_deposit(self):
        self.assertEqual(Decimal("500.00"), self.wallet1.balance)
        url = f"/wallets/{self.wallet1.id}/deposits/"
        data = {
            "amount": 200
        }
        response = self.client.post(url, data=data,
                                    HTTP_AUTHORIZATION='Token ' + str(self.token),
                                    content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.wallet1.refresh_from_db()
        self.assertEqual(Decimal("700.00"), self.wallet1.balance)

    def test_withdrawal(self):
        self.assertEqual(Decimal("500.00"), self.wallet1.balance)
        self.assertEqual(Decimal("0.00"), self.wallet2.balance)
        url = f"/wallets/{self.wallet1.id}/withdrawals/{self.wallet2.id}/"
        data = {
            "amount": 100
        }
        response = self.client.post(url, data=data,
                                    HTTP_AUTHORIZATION='Token ' + str(self.token),
                                    content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.wallet1.refresh_from_db()
        self.wallet2.refresh_from_db()
        self.assertEqual(Decimal("400.00"), self.wallet1.balance)
        self.assertEqual(Decimal("100.00"), self.wallet2.balance)

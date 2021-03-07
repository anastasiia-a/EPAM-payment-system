from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from wallets.models import Wallet, Operation


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
        self.operation = Operation.objects.create(name='deposit', wallet=self.wallet1,
                                                  amount=Decimal("500.00"))
        self.invalid_id = 300

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

    def test_invalid_deposit(self):
        test_cases = (
            2000000000,
            0,
            -200,
        )
        url = f"/wallets/{self.wallet1.id}/deposits/"
        for amount in test_cases:
            with self.subTest(i=amount):
                self.assertEqual(Decimal("500.00"), self.wallet1.balance)
                data = {
                    "amount": amount
                }
                response = self.client.post(url, data=data,
                                            HTTP_AUTHORIZATION='Token ' + str(self.token),
                                            content_type='application/json')
                self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
                self.wallet1.refresh_from_db()
                self.assertEqual(Decimal("500.00"), self.wallet1.balance)

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

    def test_invalid_withdrawal(self):
        test_cases = (
            1000000000,
            0,
            -100,
        )
        url = f"/wallets/{self.wallet1.id}/withdrawals/{self.wallet2.id}/"
        for amount in test_cases:
            with self.subTest(i=amount):
                self.assertEqual(Decimal("500.00"), self.wallet1.balance)
                self.assertEqual(Decimal("0.00"), self.wallet2.balance)
                data = {
                    "amount": amount
                }
                response = self.client.post(url, data=data,
                                            HTTP_AUTHORIZATION='Token ' + str(self.token),
                                            content_type='application/json')
                self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
                self.wallet1.refresh_from_db()
                self.wallet2.refresh_from_db()
                self.assertEqual(Decimal("500.00"), self.wallet1.balance)
                self.assertEqual(Decimal("0.00"), self.wallet2.balance)

    def test_get_transactions_without_token(self):
        url = f"/operations/{self.wallet1.id}/"
        response = self.client.get(url, content_type='application/json')
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_get_transactions_the_wallet(self):
        url = f"/operations/{self.wallet1.id}/"
        response = self.client.get(url, HTTP_AUTHORIZATION='Token ' + str(self.token),
                                   content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_get_transactions_the_invalid_wallet(self):
        url = f"/operations/{self.invalid_id}/"
        response = self.client.get(url, HTTP_AUTHORIZATION='Token ' + str(self.token),
                                   content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)


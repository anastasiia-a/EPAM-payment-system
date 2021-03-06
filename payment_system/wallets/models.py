import datetime
from decimal import Decimal

from django.db import models


class Wallet(models.Model):
    name = models.CharField(max_length=255, unique=True)
    client_firstname = models.CharField(max_length=30)
    client_surname = models.CharField(max_length=30)
    balance = models.DecimalField(max_digits=9, decimal_places=2, default=Decimal("0.00"))

    def __str__(self):
        return self.name


class Operation(models.Model):
    name = models.CharField(max_length=10)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.date.today())
    amount = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return f'{self.date}: {self.name} - amount={self.amount}'

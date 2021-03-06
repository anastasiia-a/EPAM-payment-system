# Generated by Django 3.1.7 on 2021-03-06 22:36

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0009_auto_20210306_1828'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='balance',
            field=models.DecimalField(decimal_places=2,
                                      default=Decimal('0.00'),
                                      max_digits=9,
                                      validators=[django.core.validators.MaxValueValidator
                                                  (Decimal('9999999.99'))]),
        ),
    ]

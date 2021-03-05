# Generated by Django 3.1.7 on 2021-03-05 12:55

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0007_auto_20210305_0806'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=9),
        ),
    ]

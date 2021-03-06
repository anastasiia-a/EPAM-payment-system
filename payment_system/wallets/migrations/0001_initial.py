# Generated by Django 3.1.7 on 2021-02-28 17:17

from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16, unique=True)),
                ('client_firstname', models.CharField(max_length=30)),
                ('client_surname', models.CharField(max_length=30)),
                ('balance', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=7)),
            ],
        ),
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('1', 'withdrawal'), ('2', 'deposit')], max_length=10)),
                ('date', models.DateField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=5)),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wallets.wallet')),
            ],
        ),
    ]

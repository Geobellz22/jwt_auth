# Generated by Django 5.1.5 on 2025-03-25 09:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('EditAccount', '0002_remove_editaccount_wallet_address_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='editaccount',
            name='bitcoin_cash_wallet',
        ),
    ]

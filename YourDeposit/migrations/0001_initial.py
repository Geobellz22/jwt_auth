# Generated by Django 4.2.4 on 2024-09-12 22:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Deposit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('wallet_type', models.CharField(max_length=50)),
                ('wallet_address', models.CharField(max_length=255)),
                ('status', models.CharField(default='confirmed', max_length=20)),
                ('transaction_id', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='your_deposits', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

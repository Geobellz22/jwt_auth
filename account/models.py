# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    use_in_migration = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is Required')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff = True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser = True')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    name = models.CharField(max_length=250)
    is_user = models.BooleanField(default=True)
    
    # Wallet fields
    Bitcoin_wallet = models.CharField(max_length=250, blank=True, null=True)
    Tether_usdt_trc20_wallet = models.CharField(max_length=250, blank=True, null=True)
    Tron_wallet = models.CharField(max_length=250, blank=True, null=True)
    Etherum_wallet = models.CharField(max_length=250, blank=True, null=True)
    Bnb_wallet = models.CharField(max_length=250, blank=True, null=True)
    Dogecoin_wallet = models.CharField(max_length=250, blank=True, null=True)
    Usdt_erc20_wallet = models.CharField(max_length=250, blank=True, null=True)
    Bitcoin_cash_wallet = models.CharField(max_length=250, blank=True, null=True)
    Tether_erc20_wallet = models.CharField(max_length=250, blank=True, null=True)
    Shiba_wallet = models.CharField(max_length=250, blank=True, null=True)

    confirmation_code = models.CharField(max_length=8, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
    
    objects = UserManager()
    

    def __str__(self):
        return f'User {self.username} - {self.email}'

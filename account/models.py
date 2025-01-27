from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
import random


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    name = models.CharField(max_length=250)
    is_user = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Wallet fields
    bitcoin_wallet = models.CharField(max_length=250, blank=True, null=True)
    tether_usdt_trc20_wallet = models.CharField(max_length=250, blank=True, null=True)
    tron_wallet = models.CharField(max_length=250, blank=True, null=True)
    ethereum_wallet = models.CharField(max_length=250, blank=True, null=True)
    bnb_wallet = models.CharField(max_length=250, blank=True, null=True)
    dogecoin_wallet = models.CharField(max_length=250, blank=True, null=True)
    usdt_erc20_wallet = models.CharField(max_length=250, blank=True, null=True)
    bitcoin_cash_wallet = models.CharField(max_length=250, blank=True, null=True)
    tether_erc20_wallet = models.CharField(max_length=250, blank=True, null=True)
    shiba_wallet = models.CharField(max_length=250, blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'User {self.username} - {self.email}'


class ConfirmationCode(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='confirmation_code'  # Unique related_name
    )
    code = models.CharField(max_length=7)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f'Confirmation Code for {self.user.username}'

    def generate_code(self):
        """Generates a new confirmation code and updates expiration time."""
        self.code = f"{random.randint(1000000, 9999999)}"
        self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        self.save()

    def is_valid(self):
        """Checks if the confirmation code is still valid."""
        return self.code and not self.is_used and self.expires_at > timezone.now()

    def invalidate(self):
        """Marks the confirmation code as used."""
        self.is_used = True
        self.save()

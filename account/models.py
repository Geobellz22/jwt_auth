from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field is required')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)  # Set default for active users
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    name = models.CharField(max_length=250)
    is_user = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)  # Use this for account activation
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

    confirmation_code = models.CharField(max_length=8, blank=True, null=True)

    # Add related_name to resolve conflicts
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

    objects = UserManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'User {self.username} - {self.email}'

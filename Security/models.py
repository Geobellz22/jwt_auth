from django.db import models
from django.conf import settings
from django.utils import timezone
import random
import string
import uuid

# Create your models here.
class Security(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    IP_SENSITIVITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('paranoid', 'Paranoid'),
    ]
    ip_address_sensitivity = models.CharField(
        max_length=20,
        choices=IP_SENSITIVITY_CHOICES,
        default='disabled'
    )
    detect_device_change = models.BooleanField(default=False)
    email_verification_code = models.CharField(max_length=8, blank=True, null=True)
    last_ip = models.GenericIPAddressField(blank=True, null=True)
    last_browser = models.CharField(max_length=200, blank=True, null=True)
    pin_code = models.CharField(max_length=6, blank=True, null=True)
    pin_expiration = models.DateTimeField(blank=True, null=True)
    suspicious_login_time = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Security settings for {self.user.username}"
    
    def generate__pin__code(self):
        self.pin_code = ''.join(random.choices(string.digits, k=6))
        self.pin_expiration = timezone.now() + timezone.timedelta(minutes=10)
        
    def is_pin_code_valid(self):
        if self.pin_code and self.pin_expiration:
            return self.pin_expiration > timezone.now()
        return False
    
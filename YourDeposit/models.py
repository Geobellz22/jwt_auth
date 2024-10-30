from django.db import models
#from django.contrib.auth.models import User
from django.conf import settings


class Deposit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='your_deposits')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    wallet_type = models.CharField(max_length=50)
    wallet_address = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default='confirmed')
    transaction_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Confirmed deposit of {self.amount} for {self.username}"

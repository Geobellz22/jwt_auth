from django.db import models
from django.conf import settings
#from django.utils import timezone

class Withdraw(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    wallet_type = models.CharField(max_length=50)
    wallet_address = models.CharField(max_length=255)
    transaction_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Withdraw {self.amount} - {self.wallet_type} for {self.user.user.name}"

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('investment', 'Investment')
    ]

    CURRENCIES = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('USDT', 'Tether'),
        ('BNB', 'Binance Coin'),
        ('DOGE', 'Dogecoin'),
        ('LTC', 'Litecoin'),
        ('TRC', 'Troncoin'),
        ('BCH', 'Bitcoin Cash')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    currency = models.CharField(max_length=10, choices=CURRENCIES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)  # Larger max_digits for higher values
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount} {self.currency}"

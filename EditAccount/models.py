from django.db import models
from django.conf import settings


class EditAccount(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    username = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    email_address = models.EmailField(max_length=100, unique=True)

    # Wallet addresses for different cryptocurrencies
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

    # Editable password field (though better practice is to handle password in User model)
    new_password = models.CharField(max_length=50, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"EditAccount {self.username} - {self.email_address}"

    def save(self, *args, **kwargs):
        super(EditAccount, self).save(*args, **kwargs)

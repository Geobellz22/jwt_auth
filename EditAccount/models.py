from django.db import models
from django.conf import settings

class EditAccount(models.Model):
    username = models.CharField(max_length=50, unique=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=False)  
    email_address = models.EmailField(max_length=100, unique=True)
    wallet_type = models.CharField(max_length=255)
    wallet_address = models.CharField(max_length=255, unique=True)
    new_password = models.CharField(max_length=50, editable=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return f"EditAccount {self.username} - {self.email_address}"

    def save(self, *args, **kwargs):
        super(EditAccount, self).save(*args, **kwargs)

from django.db import models
from django.conf import settings
import uuid

class ReferralLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    referred_user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    referral_code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reward_granted = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Referral by {self.referral.username} - Code: {self.referral_code}"
    
    @staticmethod
    def generate_referral_code():
        return str(uuid4())[:8].upper()
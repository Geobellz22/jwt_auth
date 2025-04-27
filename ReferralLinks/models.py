import uuid
import random
import string
from django.db import models
from django.conf import settings

class ReferralLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    referred_user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referral_link'
    )
    referral_code = models.CharField(max_length=30, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reward_granted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self.generate_unique_referral_code()
        super().save(*args, **kwargs)

    def generate_unique_referral_code(self):
        while True:
            random_digits = ''.join(random.choices(string.digits, k=5))
            username_part = self.referred_user.username.lower().replace(' ', '')
            referral_code = f"{username_part}-{random_digits}"

            if not ReferralLink.objects.filter(referral_code=referral_code).exists():
                return referral_code

    def __str__(self):
        return f"{self.referred_user.username}'s Referral Link"

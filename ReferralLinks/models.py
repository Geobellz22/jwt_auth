import uuid
from django.db import models
from django.conf import settings

class ReferralLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    referred_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='referral'
    )

    referrer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrals_made'
    )

    referral_code = models.CharField(max_length=100, unique=True, blank=True)

    referral_link = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Set referral code based on username if not set
        if not self.referral_code:
            self.referral_code = self.referred_user.username

        # Construct referral link using production or local URL
        if not self.referral_link:
            base_url = getattr(settings, 'BACKEND_BASE_URL', 'http://localhost:8000')
            self.referral_link = f"{base_url}/register/?ref={self.referral_code}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.referred_user.username}'s referral ({self.referral_link})"

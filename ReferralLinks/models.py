import uuid
from django.db import models
from django.conf import settings

class ReferralLink(models.Model):
    """
    Stores the shareable referral link for each user.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    referred_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='referral_link_record'
    )
    referrer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referral_links_made'
    )
    referral_code = models.CharField(
        max_length=100,
        unique=True,
        help_text="Typically the referrer's username"
    )
    referral_link = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        help_text="Full URL: https://yourdomain.com/register/?ref=<code>"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Ensure referral_code = username if not provided
        if not self.referral_code and self.referrer:
            self.referral_code = self.referrer.username

        # Build the full referral_link if missing
        if not self.referral_link and self.referral_code:
            base_url = getattr(settings, 'BACKEND_BASE_URL', 'http://localhost:8000')
            self.referral_link = f"{base_url}/register/?ref={self.referral_code}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.referral_link} (by {self.referrer.username if self.referrer else '—'})"
            
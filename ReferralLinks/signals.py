from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ReferralLink
from django.conf import settings

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_referral_code(sender, instance, created, **kwargs):
    if created:
        Refferal.objects.create(referrer=instance, referral_code=Referral.generate_referral_code())
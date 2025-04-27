from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from referral_link.utils import create_referral_link_for_user

@receiver(post_save, sender=User)
def create_referral_link(sender, instance, created, **kwargs):
    if created:
        create_referral_link_for_user(instance)

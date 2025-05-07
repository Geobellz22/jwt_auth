from django.db import models
from django.conf import settings

class Referral(models.Model):
    """
    Records each user-to-user referral relationship.
    """
    referrer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='referrals'
    )
    referred_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='referral_record'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(
        default=False,
        help_text="Set True when the referred user completes the activation criteria"
    )

    def __str__(self):
        return f"{self.referred_user.username} ← {self.referrer.username}"


class ReferralReward(models.Model):
    """
    Defines commission percentage for each referral level.
    """
    LEVEL_CHOICES = [
        (1, 'Level 1'),
        (2, 'Level 2'),
        (3, 'Level 3'),
        (4, 'Level 4'),
    ]

    referral = models.ForeignKey(
        Referral,
        on_delete=models.CASCADE,
        related_name='rewards'
    )
    level = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES)
    reward_percentage = models.DecimalField(
        max_digits=5, decimal_places=2,
        help_text="Commission percentage for this level"
    )

    class Meta:
        unique_together = ('referral', 'level')

    def __str__(self):
        return f"{self.referral.referrer.username} L{self.level} → {self.reward_percentage}%"


class ReferralCommission(models.Model):
    """
    Logs each actual commission earned when a referred user transacts.
    """
    referral = models.ForeignKey(
        Referral,
        on_delete=models.CASCADE,
        related_name='commissions'
    )
    source_amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        help_text="Amount on which commission was calculated"
    )
    amount_earned = models.DecimalField(
        max_digits=12, decimal_places=2,
        help_text="Commission paid out"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"${self.amount_earned} for {self.referral.referrer.username}"


class ReferralSummary(models.Model):
    """
    Cached summary per user: total referrals, actives, and commissions.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='referral_summary'
    )
    total_referrals = models.PositiveIntegerField(default=0)
    active_referrals = models.PositiveIntegerField(default=0)
    total_commission = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=0.00
    )

    def __str__(self):
        return (
            f"{self.user.username}: {self.total_referrals} referrals, "
            f"{self.active_referrals} active, ${self.total_commission}"
        )

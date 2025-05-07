# referral/signals.py

from decimal import Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F

from .models import Referral, ReferralReward, ReferralSummary, ReferralCommission
from transactions.models import Deposit   # ← adjust to your actual deposit/transaction model

# Define your commission percentages by level
COMMISSION_LEVELS = {
    1: Decimal('3.00'),
    2: Decimal('5.00'),
    3: Decimal('10.00'),
    4: Decimal('20.00'),
}

@receiver(post_save, sender=Referral)
def seed_referral_rewards(sender, instance, created, **kwargs):
    """
    When a new Referral record is created,  
    1) increment total_referrals for the level-1 referrer  
    2) create ReferralReward entries for levels 1–4 (if ancestors exist)
    """
    if not created or not instance.referrer:
        return

    # 1) Update summary: total referrals
    summary, _ = ReferralSummary.objects.get_or_create(user=instance.referrer)
    summary.total_referrals = F('total_referrals') + 1
    summary.save()

    # 2) Seed ReferralReward for each level up the chain
    ancestor = instance.referrer
    current_level = 1
    while ancestor and current_level <= 4:
        percent = COMMISSION_LEVELS.get(current_level)
        if percent is not None:
            ReferralReward.objects.create(
                referral=instance,
                level=current_level,
                reward_percentage=percent
            )
        # Move to next ancestor
        try:
            ancestor_referral = Referral.objects.get(referred=ancestor)
            ancestor = ancestor_referral.referrer
        except Referral.DoesNotExist:
            break
        current_level += 1


@receiver(post_save, sender=Deposit)
def process_referral_commission(sender, instance, created, **kwargs):
    """
    When a Deposit is made by a referred user:
    1) mark their Referral 'active' on first deposit
    2) record a ReferralCommission for each level
    3) update active_referrals and total_commission in ReferralSummary
    """
    if not created:
        return

    deposit = instance
    user = deposit.user
    amount = deposit.amount

    # 1) Find the Referral record
    try:
        referral = Referral.objects.get(referred=user)
    except Referral.DoesNotExist:
        return

    # 2) Activate the referral on the first qualifying deposit
    if not referral.is_active:
        referral.is_active = True
        referral.save()

        summary, _ = ReferralSummary.objects.get_or_create(user=referral.referrer)
        summary.active_referrals = F('active_referrals') + 1
        summary.save()

    # 3) For each ReferralReward on this referral, calculate commission
    for reward in ReferralReward.objects.filter(referral=referral):
        commission_amount = (amount * reward.reward_percentage) / Decimal('100')
        ReferralCommission.objects.create(
            referral=referral,
            amount_earned=commission_amount,
            source_amount=amount
        )

        # 4) Update the total_commission for each ancestor
        ancestor_user = reward.referral.referrer
        summary, _ = ReferralSummary.objects.get_or_create(user=ancestor_user)
        summary.total_commission = F('total_commission') + commission_amount
        summary.save()

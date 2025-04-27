
from django.db import models
from django.conf import settings

class Referral(models.Model):
    referral_code = models.CharField(max_length=6, unique=True)
    referred_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='referred_by', 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        referred_by_username = self.referred_by.username if self.referred_by else 'None'
        return f'{self.user.username} - {self.referral_code} - {referred_by_username}'


class ReferralReward(models.Model):
    LEVELS = [
        (1, 'Level 1'),
        (2, 'Level 2'),
        (3, 'Level 3'),
        (4, 'Level 4'),
    ]

    referral = models.ForeignKey(Referral, on_delete=models.CASCADE)
    level = models.IntegerField(choices=LEVELS)
    reward_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Referral Reward for {self.referral.user.username} - Level {self.level}"

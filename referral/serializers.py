from rest_framework import serializers
from .models import Referral, ReferralReward


class ReferralSerializer(serializers.ModelSerializer):
    referred_by_username = serializers.CharField(
        source='referred_by.username', read_only=True
    )

    class Meta:
        model = Referral
        fields = ['referral_code', 'referred_by', 'referred_by_username', 'created_at']
        read_only_fields = ['referral_code', 'created_at']


class ReferralRewardSerializer(serializers.ModelSerializer):
    referral_user = serializers.CharField(
        source='referral.user.username', read_only=True
    )

    class Meta:
        model = ReferralReward
        fields = ['referral', 'referral_user', 'level', 'reward_percentage']
        read_only_fields = ['reward_percentage']  # Rewards are predefined

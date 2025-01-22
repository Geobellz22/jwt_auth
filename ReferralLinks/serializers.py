from rest_framework import serializers
from .models import ReferralLink

class ReferralLinkSerializer(serializers.ModelSerializer):
    referral_link = serializers.SerializerMethodField()

    class Meta:
        model = ReferralLink
        fields = ['id', 'referred_user', 'referral_link', 'referral_code', 'created_at', 'reward_granted']
        read_only_fields = ('referred_user', 'referral_code', 'created_at', 'reward_granted')

    def get_referral_link(self, obj):
        # Generate the full referral link using referral_code
        from django.conf import settings
        return f"{settings.SITE_URL}/referral/{obj.referral_code}"

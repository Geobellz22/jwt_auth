from rest_framework import serializers
from .models import ReferralSummary

class ReferralStatsSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ReferralSummary
        fields = ['username', 'total_referrals', 'active_referrals', 'total_commission']

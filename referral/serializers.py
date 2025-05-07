from rest_framework import serializers
from .models import ReferralSummary

class ReferralStatsSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    """
    Serializer for ReferralSummary model to return referral statistics.
    """
    class Meta:
        model = ReferralSummary
        fields = ['user', 'total_referrals', 'active_referrals', 'total_commission']
        
        read_only_fields = fields

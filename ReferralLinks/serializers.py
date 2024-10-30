from rest_framework import serializers
from .models import ReferralLink

class ReferralLink(serializers.ModelSerializer):
    class Meta:
        model = ReferralLink
        fields = ['id', 'user', 'referral_link', 'referral_code', 'created_at', 'reward_granted']
        read_only_fields = ('referral_code', 'created_at', 'reward_granted')
        
        def validate_referred_user(self, value):
            if value:
                return serializers.ValidationError("You can't manually set referred user.")
            return value 
        
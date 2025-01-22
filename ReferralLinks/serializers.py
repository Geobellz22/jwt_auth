from rest_framework import serializers
from .models import ReferralLink

class ReferralLinkSerializer(serializers.ModelSerializer):
    referral_link = serializers.SerializerMethodField()

    class Meta:
        model = ReferralLink
        fields = ['id', 'referred_user', 'referral_link', 'referral_code', 'created_at', 'reward_granted']
        read_only_fields = ('referral_code', 'created_at', 'reward_granted')

    def get_referral_link(self, obj) -> str:
        """
        Generate the full referral link for the given object.
        """
        request = self.context.get('request')
        if request is not None:
            # Example: Generating the referral link with a base URL
            return f"{request.scheme}://{request.get_host()}/referral/{obj.referral_code}"
        return ""

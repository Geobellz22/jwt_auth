from rest_framework import serializers
from .models import ReferralLink

class ReferralLinkSerializer(serializers.ModelSerializer):
    referral_link = serializers.SerializerMethodField()
    

    class Meta:
        model = ReferralLink
        fields = ['id', 'referred_user', 'referrer', 'referral_code', 'referral_link', 'created_at']

    def get_referral_link(self, obj) -> str:
        request = self.context.get('request')
        if request:
            return f"{request.scheme}://{request.get_host()}/register/?ref={obj.referral_code}"
        return None


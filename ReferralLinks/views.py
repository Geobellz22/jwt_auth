from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ReferralLinkSerializer
from .models import ReferralLink

class ReferralLinkView(APIView):
    def get(self, request, format=None):
        try:
            referral_link = ReferralLink.objects.get(user=request.user)  # Assuming user-specific referral links
            serializer = ReferralLinkSerializer(referral_link)
            return Response(serializer.data)
        except ReferralLink.DoesNotExist:
            return Response({"error": "ReferralLink not found"}, status=status.HTTP_404_NOT_FOUND)

class RegistrationWithReferralView(APIView):
    def post(self, request, format=None):
        referral_code = request.data.get('referral_code')

        if not referral_code:
            return Response({"error": "Referral code is missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            referral = ReferralLink.objects.get(referral_code=referral_code)
            referral.referred_user = request.user  # Assuming `referred_user` field exists in the model
            referral.save()
            return Response({"message": "Referral successfully registered"}, status=status.HTTP_200_OK)
        except ReferralLink.DoesNotExist:
            return Response({"error": "Invalid referral code"}, status=status.HTTP_400_BAD_REQUEST)

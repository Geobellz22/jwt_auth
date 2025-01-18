from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ReferralLink
from .models import ReferralLink

# Create your views here.
class ReferralLinkView(APIView):
    def get(self, request, format=None):
        referral_links = ReferralLink.objects.all()
        try:
            referral_link = Referral_link.objects.get(referral_link=request.user)
            serializer = ReferralLinkSerializer(referral_link)
            return Response(serializer.data)
        except ReferralLink.DoesNotExist:
            return Response({"error: ReferralLink not found"}, status=status.HTTP_404_NOT_FOUND)
        
class RegistrationWithReferralView(APIView):
    def post(self, request, format=None):
        referral_code = request.data.get('referral_code')
        
        if referral_code:
            try:
                referral = Referral.objects.get(referral_code=referral_code)
                referral.referred_user = request.user
                referral.save()
                
                return Response({"message: Referral sucessefully registered"}, status=status.HTTP_200_OK)
            except ReferralLink.DoesNotExist:
                return Response({"error: Invalid Referral code"}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({"error: Referral code is missing"}, status=status.HTTP_400_BAD_REQUEST)
            
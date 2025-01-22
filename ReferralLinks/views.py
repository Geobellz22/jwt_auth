from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import ReferralLinkSerializer
from .models import ReferralLink

class ReferralLinkView(APIView):
    """
    View to retrieve the referral link for the authenticated user.
    """
    permission_classes = [IsAuthenticated]  # Require user authentication

    def get(self, request, format=None):
        try:
            # Retrieve the referral link for the logged-in user
            referral_link = ReferralLink.objects.get(referred_user=request.user)  # Fixed field name
            serializer = ReferralLinkSerializer(referral_link)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ReferralLink.DoesNotExist:
            # Handle case where referral link does not exist for the user
            return Response(
                {"error": "Referral link not found for this user"},
                status=status.HTTP_404_NOT_FOUND
            )


class RegistrationWithReferralView(APIView):
    """
    View to handle registration with a referral code.
    """
    permission_classes = [IsAuthenticated]  # Require user authentication

    def post(self, request, format=None):
        # Extract the referral code from the request data
        referral_code = request.data.get('referral_code')

        if not referral_code:
            # Handle case where referral code is missing
            return Response(
                {"error": "Referral code is missing"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Retrieve the referral link associated with the given referral code
            referral = ReferralLink.objects.get(referral_code=referral_code)

            # Ensure the referral link is not already assigned to another user
            if referral.referred_user is not None:
                return Response(
                    {"error": "This referral code has already been used"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Assign the referred user to the referral link
            referral.referred_user = request.user
            referral.save()

            return Response(
                {"message": "Referral successfully registered"},
                status=status.HTTP_200_OK
            )
        except ReferralLink.DoesNotExist:
            # Handle case where the referral code is invalid
            return Response(
                {"error": "Invalid referral code"},
                status=status.HTTP_400_BAD_REQUEST
            )

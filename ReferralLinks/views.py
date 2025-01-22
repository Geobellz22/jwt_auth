from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from .serializers import ReferralLinkSerializer
from .models import ReferralLink
from drf_spectacular.utils import extend_schema, OpenApiResponse

class ReferralCodeInputSerializer(serializers.Serializer):
    referral_code = serializers.CharField(required=True)

class ReferralLinkView(GenericAPIView):
    """
    View to retrieve the referral link for the authenticated user.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ReferralLinkSerializer

    @extend_schema(
        responses={
            200: ReferralLinkSerializer,
            404: OpenApiResponse(description="Referral link not found")
        }
    )
    def get(self, request, format=None):
        try:
            referral_link = ReferralLink.objects.get(referred_user=request.user)
            serializer = self.get_serializer(referral_link)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ReferralLink.DoesNotExist:
            return Response(
                {"error": "Referral link not found for this user"},
                status=status.HTTP_404_NOT_FOUND
            )

class RegistrationWithReferralView(GenericAPIView):
    """
    View to handle registration with a referral code.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ReferralCodeInputSerializer

    @extend_schema(
        request=ReferralCodeInputSerializer,
        responses={
            200: OpenApiResponse(description="Referral successfully registered"),
            400: OpenApiResponse(description="Invalid referral code or already used"),
        }
    )
    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        referral_code = serializer.validated_data['referral_code']

        try:
            referral = ReferralLink.objects.get(referral_code=referral_code)

            if referral.referred_user is not None:
                return Response(
                    {"error": "This referral code has already been used"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            referral.referred_user = request.user
            referral.save()

            return Response(
                {"message": "Referral successfully registered"},
                status=status.HTTP_200_OK
            )
        except ReferralLink.DoesNotExist:
            return Response(
                {"error": "Invalid referral code"},
                status=status.HTTP_400_BAD_REQUEST
            )

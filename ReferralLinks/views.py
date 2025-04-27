from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import ReferralLink
from .serializers import ReferralLinkSerializer

class ReferralCodeInputSerializer(serializers.Serializer):
    referral_code = serializers.CharField(required=True)

class ReferralLinkView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReferralLinkSerializer

    @extend_schema(
        responses={
            200: ReferralLinkSerializer
        }
    )
    def get(self, request, *args, **kwargs):
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
    permission_classes = [IsAuthenticated]
    serializer_class = ReferralCodeInputSerializer

    @extend_schema(
        request=ReferralCodeInputSerializer,
        responses={
            200: OpenApiResponse(description="Referral successfully registered"),
            400: OpenApiResponse(description="Invalid referral code or already used"),
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        referral_code = serializer.validated_data['referral_code']

        try:
            referral = ReferralLink.objects.get(referral_code=referral_code)

            if referral.referred_user == request.user:
                return Response(
                    {"error": "You cannot refer yourself."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if request.user.referral_link.reward_granted:
                return Response(
                    {"error": "You have already used a referral code."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Mark the referral as rewarded
            referral.reward_granted = True
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

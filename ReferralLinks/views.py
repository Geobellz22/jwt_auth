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


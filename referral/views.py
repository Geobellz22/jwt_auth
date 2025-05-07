from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import ReferralSummary
from .serializers import ReferralStatsSerializer

class ReferralSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            summary = ReferralSummary.objects.get(user=request.user)
        except ReferralSummary.DoesNotExist:
            summary = ReferralSummary.objects.create(user=request.user)

        serializer = ReferralStatsSerializer(summary)
        return Response(serializer.data, status=status.HTTP_200_OK)

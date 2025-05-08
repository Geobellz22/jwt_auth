from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import ReferralSummary
from .serializers import ReferralStatsSerializer

class ReferralSummaryView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReferralStatsSerializer

    def get(self, request):
        user = request.user

        # Safely get or create ReferralSummary for the authenticated user
        summary, _ = ReferralSummary.objects.get_or_create(user=user)

        # Use the correct serializer
        serializer = ReferralStatsSerializer(summary)
        return Response(serializer.data, status=status.HTTP_200_OK)

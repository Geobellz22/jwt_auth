from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Withdraw
from .serializers import WithdrawSerializer
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
import logging

# Set up logging for better debugging
logger = logging.getLogger(__name__)

class WithdrawView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WithdrawSerializer  
    def post(self, request, format=None):
        user = request.user
        logger.debug(f"User: {user.username}, Data: {request.data}")

        # Regular User: Create new withdrawal request
        if not user.is_staff:
            serializer = WithdrawSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                # Withdrawal creation happens in the serializer itself after validation
                withdraw = serializer.save(user=user, status='pending')
                logger.debug(f"Withdrawal created successfully: {withdraw.id}")
                return Response({
                    "message": "Withdrawal request created successfully",
                    "withdrawal_id": withdraw.id
                }, status=status.HTTP_201_CREATED)
            logger.error(f"Validation errors: {serializer.errors}")  # Log errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Admin: Update withdrawal status
        if user.is_staff:
            withdraw_id = request.data.get('withdrawal_id')
            status_update = request.data.get('status')

            if not withdraw_id or not status_update:
                return Response({"error": "Withdrawal ID and status are required"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                withdraw = Withdraw.objects.get(id=withdraw_id)
            except ObjectDoesNotExist:
                return Response({"error": "Withdrawal request not found"}, status=status.HTTP_404_NOT_FOUND)

            if withdraw.status != 'pending':
                return Response({"error": "Only pending withdrawals can be updated"}, status=status.HTTP_400_BAD_REQUEST)

            if status_update in ['processed', 'rejected']:
                withdraw.status = status_update
                withdraw.save()
                logger.debug(f"Withdrawal status updated: {withdraw.id} to {status_update}")
                return Response({"message": f"Withdrawal status updated to {status_update}"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid status. Must be 'processed' or 'rejected'"}, status=status.HTTP_400_BAD_REQUEST)

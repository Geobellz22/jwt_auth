from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .models import Withdraw
from .serializers import WithdrawSerializer
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist

class WithdrawView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        # Regular User: Create new withdrawal request
        if not request.user.is_staff:
            serializer = WithdrawSerializer(data=request.data)
            if serializer.is_valid():
                if request.user.balance >= serializer.validated_data['amount']:
                    withdraw = serializer.save(user=request.user, status='pending')
                    return Response({"message": "Withdrawal request created successfully", "withdrawal_id": withdrawal.id}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        if request.user.is_staff:
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
                return Response({"message": f"Withdrawal status updated to {status_update}"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid status. Must be 'processed' or 'rejected'"}, status=status.HTTP_400_BAD_REQUEST)


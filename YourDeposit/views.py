from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Deposit
from .serializers import DepositSerializer

class YourDeposit(APIView):
    def get(self, request):
        user = request.user
        deposits = Deposits.objects.filter(user=user, status='confirmed')
        
        total_deposit = sum(deposit.amount for deposit in deposits)
        
        return Response({
            'total_deposit': total_deposit,
             'deposits': DepositSerializer(deposits, many=True).data
        })
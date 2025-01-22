from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Deposit
from .serializers import DepositSerializer

class YourDeposit(APIView):
    """
    View to retrieve confirmed deposits for the authenticated user.
    """
    def get(self, request):
        user = request.user
        
        # Fetch all confirmed deposits for the user
        deposits = Deposit.objects.filter(user=user, status='confirmed')
        
        # Calculate total deposit directly in the database
        total_deposit = deposits.aggregate(total=models.Sum('amount'))['total'] or 0

        # Serialize the deposits and return the response
        return Response(
            {
                'total_deposit': total_deposit,
                'deposits': DepositSerializer(deposits, many=True).data
            },
            status=status.HTTP_200_OK
        )

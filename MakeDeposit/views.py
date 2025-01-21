from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Deposit
from .serializers import DepositSerializer

class MakeDeposit(APIView):
    def post(self, request):
        user = request.user
        amount = request.data.get('amount')
        wallet_type = request.data.get('wallet_type')
        
        wallet_addresses = {
            'Bitcoin': 'bc1q372ruvgmqa0uwumdzqsvgvc6z2w030pxvkw4ww',
            'Ethereum': '0x1a158E08B0bd1ac5D991e85e3A9Dd373D21a1489',
            'Tron': 'TB9JQFM5Jndp6hqvxvQvKa5RrbrprDkJVo',
            'Tether usdt Trc20': 'TB9JQFM5Jndp6hqvxvQvKa5RrbrprDkJVo',
            'Tether erc 20': '0x1a158E08B0bd1ac5D991e85e3A9Dd373D21a1489',
            'Bnb': '0x1a158E08B0bd1ac5D991e85e3A9Dd373D21a1489',
            'Dogecoin': 'DEereXL4WAi4MNcVdCfTcBPMEB1a5UFMUe',
            'Litecoin': 'ltc1q46nn6wg3z6wvsnwdfysn4sqqxnvk3uqfps2g3d',
            'Shiba': 'BDKbzpgY7GGE9iQEgrhZRborx7zvGDsaWLKHm4VwBtpn',
        }

        if wallet_type not in wallet_addresses:
            return Response({'error': 'Invalid wallet type'}, status=status.HTTP_400_BAD_REQUEST)

        if not amount or float(amount) <= 0:
            return Response({'error': 'Invalid or missing deposit amount'}, status=status.HTTP_400_BAD_REQUEST)

        wallet_address = wallet_addresses[wallet_type]
        deposit = Deposit.objects.create(
            user=user,
            amount=amount,
            wallet_type=wallet_type,
            wallet_address=wallet_address,
            status='pending'
        )

        return Response({
            'wallet_address': wallet_address,
            'transaction_id': deposit.transaction_id,
            'message': 'Please send funds to the provided wallet address.'
        }, status=status.HTTP_201_CREATED)

class ConfirmDeposit(APIView):
    def post(self, request):
        user = request.user
        transaction_id = request.data.get('transaction_id')

        if not transaction_id:
            return Response({'error': 'Transaction ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            deposit = Deposit.objects.get(transaction_id=transaction_id, user=user)

            if deposit.status == 'confirmed':
                return Response({'message': 'Deposit is already confirmed'}, status=status.HTTP_200_OK)

            deposit.status = 'confirmed'
            deposit.save()

            return Response({'status': 'success', 'message': 'Deposit confirmed'}, status=status.HTTP_200_OK)

        except Deposit.DoesNotExist:
            return Response({'error': 'Invalid transaction ID or deposit does not exist'}, status=status.HTTP_404_NOT_FOUND)

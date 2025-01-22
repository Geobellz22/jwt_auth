from rest_framework import serializers
from .models import Deposit

class YourDepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = ['user', 'amount', 'wallet_type', 'wallet_address', 'status', 'transaction_id', 'created_at    ' ]

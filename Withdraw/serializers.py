from rest_framework import serializers
from .models import Withdraw

class WithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdraw
        fields = ['user', 'amount', 'wallet_address', 'wallet_type', 'status', 'transaction_id', 'created_at']
        read_only_fields = ['status', 'transaction_id', 'created_at']

    def validate(self, data):
        user_balance = self.context['request'].user.profile.balance
        if data['amount'] > user_balance:
            raise serializers.ValidationError({'amount': 'Insufficient balance for this withdrawal'})
        return data

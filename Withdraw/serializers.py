from rest_framework import serializers
from .models import Withdraw

class WithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdraw
        fields = ['user', 'amount', 'wallet_address', 'wallet_type', 'status', 'transaction_id', 'created_at']
        read_only_fields = ['status', 'transaction_id', 'created_at']

    def validate(self, data):
        # Ensure the user has a profile and can access the balance
        user_profile = self.context['request'].user.profile
        if not user_profile:
            raise serializers.ValidationError({'user': 'User profile not found'})
        
        # Check for sufficient balance
        user_balance = user_profile.balance
        if data['amount'] > user_balance:
            raise serializers.ValidationError({'amount': 'Insufficient balance for this withdrawal'})
        
        return data

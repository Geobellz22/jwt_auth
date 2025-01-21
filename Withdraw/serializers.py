from rest_framework import serializers
from .models import Withdraw

class WithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdraw
        fields = ['user', 'amount', 'wallet_address', 'wallet_type', 'status', 'transaction_id', 'created_at']
        read_only_fields = ['status', 'transaction_id', 'created_at']

    def validate(self, data):
        # Ensure the request context is correctly passed for balance check
        user = self.context['request'].user
        user_profile = getattr(user, 'profile', None)  # Get profile from user
        
        if user_profile is None:
            raise serializers.ValidationError({'user': 'User profile not found'})

        # Check if user balance is available
        user_balance = user_profile.balance if user_profile.balance is not None else 0
        
        # Debug logging (Optional)
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"User balance: {user_balance}, Withdrawal amount: {data['amount']}")

        if data['amount'] > user_balance:
            raise serializers.ValidationError({'amount': 'Insufficient balance for this withdrawal'})

        return data

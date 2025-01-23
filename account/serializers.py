from rest_framework import serializers
from .models import User
from django.utils import timezone


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'name',
            'is_user',
            'is_admin',
            'is_verified',
            'created_at',
            'updated_at',
            'bitcoin_wallet',
            'tether_usdt_trc20_wallet',
            'tron_wallet',
            'ethereum_wallet',
            'bnb_wallet',
            'dogecoin_wallet',
            'usdt_erc20_wallet',
            'bitcoin_cash_wallet',
            'tether_erc20_wallet',
            'shiba_wallet',
            'confirmation_code',
            'confirmation_code_expires_at',
        ]
        read_only_fields = ['confirmation_code', 'confirmation_code_expires_at', 'is_verified', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'name']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ConfirmationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    confirmation_code = serializers.CharField(max_length=7)

    def validate(self, data):
        email = data.get('email')
        code = data.get('confirmation_code')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        if not user.is_confirmation_code_valid(code):
            raise serializers.ValidationError("Invalid or expired confirmation code.")

        return data

    def save(self):
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        user.invalidate_confirmation_code()
        return user

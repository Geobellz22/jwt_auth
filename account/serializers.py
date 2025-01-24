from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from account.models import User, ConfirmationCode
import random
import string


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['email'] = user.email
        token['username'] = user.username
        token['name'] = user.name
        token['is_active'] = user.is_active
        token['is_verified'] = user.is_verified
        return token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'name',
            'is_user', 'password', 'bitcoin_wallet',
            'tether_usdt_trc20_wallet', 'tron_wallet',
            'ethereum_wallet', 'bnb_wallet', 'dogecoin_wallet',
            'usdt_erc20_wallet', 'bitcoin_cash_wallet', 'shiba_wallet',
        ]
        read_only_fields = ['is_user']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'username': {'required': True}
        }

    def create(self, validated_data):
        # Extract password and remove it from the validated data
        password = validated_data.pop('password')

        # Create the user
        user = User.objects.create(**validated_data)

        # Set the password securely
        user.set_password(password)
        user.save()

        # Generate and link a confirmation code
        confirmation = ConfirmationCode.objects.create(user=user)
        confirmation.generate_code()

        return user

    def validate_email(self, value):
        # Ensure email is unique
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        # Ensure username is unique
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value


class ConfirmEmailSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    confirmation_code = serializers.CharField(max_length=7, required=True)

    def validate(self, data):
        try:
            user = User.objects.get(id=data['user_id'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid user or code.")

        # Check if confirmation code exists and is valid
        confirmation = user.confirmation_code
        if not confirmation or not confirmation.is_valid() or confirmation.code != data['confirmation_code']:
            raise serializers.ValidationError("Invalid or expired confirmation code.")

        return data

    def save(self):
        user = User.objects.get(id=self.validated_data['user_id'])

        # Verify the user
        user.is_active = True
        user.is_verified = True
        user.save()

        # Invalidate the confirmation code
        user.confirmation_code.invalidate()
        return user

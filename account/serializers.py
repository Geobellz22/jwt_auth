from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from account.models import User


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.email
        token['username'] = user.username
        token['name'] = user.name
        token['is_active'] = user.is_active

        return token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'confirmation_code', 'name', 
            'is_user', 'password', 'bitcoin_wallet', 'tether_usdt_trc20_wallet', 
            'tron_wallet', 'ethereum_wallet', 'bnb_wallet', 'dogecoin_wallet', 
            'usdt_erc20_wallet', 'bitcoin_cash_wallet', 'shiba_wallet'
        ]
        read_only_fields = ['is_user']
        extra_kwargs = {
            'password': {'write_only': True}
        }
        
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            name=validated_data['name'],
            is_user=True,
            bitcoin_wallet=validated_data.get('bitcoin_wallet'),
            tether_usdt_trc20_wallet=validated_data.get('tether_usdt_trc20_wallet'),
            tron_wallet=validated_data.get('tron_wallet'),
            ethereum_wallet=validated_data.get('ethereum_wallet'),
            bnb_wallet=validated_data.get('bnb_wallet'),
            dogecoin_wallet=validated_data.get('dogecoin_wallet'),
            usdt_erc20_wallet=validated_data.get('usdt_erc20_wallet'),
            bitcoin_cash_wallet=validated_data.get('bitcoin_cash_wallet'),
            shiba_wallet=validated_data.get('shiba_wallet'),
        )
        
        user.set_password(validated_data['password'])
        user.save()
        return user
        
    def get_fields(self):
        fields = super().get_fields()
        if self.instance:
            fields['email'].read_only = True
        return fields


class ConfirmEmailSerializer(serializers.Serializer):
    confirmation_code = serializers.CharField(max_length=4)

    def validate_confirmation_code(self, value):
        try:
            user = User.objects.get(confirmation_code=value, is_active=False)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired confirmation code.")
        return user

    def save(self):
        user = self.validated_data['confirmation_code']
        user.is_active = True
        user.confirmation_code = ""
        user.save()
        return user

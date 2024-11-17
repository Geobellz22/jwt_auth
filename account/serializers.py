from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from account.models import User

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
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
            'usdt_erc20_wallet', 'bitcoin_cash_wallet'
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
            Bitcoin_wallet=validated_data.get('bitcoin_wallet'),
            tether_usdt_trc20_wallet=validated_data.get('tether_usdt_trc20_wallet'),
            tron_wallet=validated_data.get('tron_wallet'),
            etherum_wallet=validated_data.get('etherum_wallet'),
            bnb_wallet=validated_data.get('bnb_wallet'),
            dogecoin_wallet=validated_data.get('dogecoin_wallet'),
            usdt_erc20_wallet=validated_data.get('usdt_erc20_wallet'),
            bitcoin_cash_wallet=validated_data.get('bitcoin_cash_wallet'),
        )
        
        user.set_password(validated_data['password'])
        user.save()
        return user
        
    def get_fields(self):
        fields = super().get_fields()
        if self.instance:
            fields['email'].read_only = True
        return fields

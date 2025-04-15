from rest_framework import serializers
from .models import EditAccount
from account.models import User


class UserRegisteredDetailsSerializer(serializers.ModelSerializer):
    bitcoin_wallet = serializers.SerializerMethodField()
    ethereum_wallet = serializers.SerializerMethodField()
    tether_usdt_trc20_wallet = serializers.SerializerMethodField()
    bnb_wallet = serializers.SerializerMethodField()
    dogecoin_wallet = serializers.SerializerMethodField()
    tron_wallet = serializers.SerializerMethodField()
    bitcoin_cash_wallet = serializers.SerializerMethodField()
    shiba_wallet = serializers.SerializerMethodField()
    litecoin_wallet = serializers.SerializerMethodField()
    tether_erc20_wallet = serializers.SerializerMethodField()
    password = serializers.CharField(required=True)
    username = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'name', 'password',
            'bitcoin_wallet', 'tether_usdt_trc20_wallet', 'tron_wallet',
            'ethereum_wallet', 'bnb_wallet', 'dogecoin_wallet',
            'litecoin_wallet', 'bitcoin_cash_wallet',
            'tether_erc20_wallet', 'shiba_wallet',
        ]
        read_only_fields = fields

    def get_bitcoin_wallet(self, obj) -> str:
        return obj.bitcoin_wallet

    def get_ethereum_wallet(self, obj) -> str:
        return obj.ethereum_wallet

    def get_tether_usdt_trc20_wallet(self, obj) -> str:
        return obj.tether_usdt_trc20_wallet

    def get_bnb_wallet(self, obj) -> str:
        return obj.bnb_wallet

    def get_dogecoin_wallet(self, obj) -> str:
        return obj.dogecoin_wallet

    def get_tron_wallet(self, obj) -> str:
        return obj.tron_wallet

    def get_bitcoin_cash_wallet(self, obj) -> str:
        return obj.bitcoin_cash_wallet

    def get_shiba_wallet(self, obj) -> str:
        return obj.shiba_wallet

    def get_litecoin_wallet(self, obj) -> str:
        return obj.litecoin_wallet

    def get_tether_erc20_wallet(self, obj) -> str:
        return obj.tether_erc20_wallet


class EditAccountSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(write_only=True, required=False)
    name = serializers.CharField(required=True)
    new_password = serializers.CharField(write_only=True, required=False)
    retype_password = serializers.CharField(write_only=True, required=False)
    username = serializers.CharField(required=True)
    email_address = serializers.EmailField(required=True)

    class Meta:
        model = EditAccount
        fields = [
            'username', 'name', 'email_address', 'bitcoin_wallet', 'tether_usdt_trc20_wallet', 'tron_wallet',
            'ethereum_wallet', 'bnb_wallet', 'dogecoin_wallet', 'bitcoin_cash_wallet',
            'tether_erc20_wallet', 'shiba_wallet', 'litecoin_wallet', 'new_password', 'retype_password',
            'created_at', 'updated_at', 'current_password',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_username(self, value):
        if EditAccount.objects.exclude(pk=self.instance.pk).filter(username=value).exists():
            raise serializers.ValidationError("This username is already in use.")
        return value

    def validate_name(self, value):
        if EditAccount.objects.exclude(pk=self.instance.pk).filter(name=value).exists():
            raise serializers.ValidationError("This name is already in use.")
        return value

    def validate_email_address(self, value):
        if EditAccount.objects.exclude(pk=self.instance.pk).filter(email_address=value).exists():
            raise serializers.ValidationError("This email address is already in use.")
        return value

    def validate_wallet(self, field_name, value):
        if value:
            if len(value) > 250:
                raise serializers.ValidationError(
                    f"{field_name.replace('_', ' ').capitalize()} address is too long (maximum is 250 characters)."
                )
            if EditAccount.objects.exclude(pk=self.instance.pk).filter(**{field_name: value}).exists():
                raise serializers.ValidationError(f"This {field_name.replace('_', ' ')} is already in use.")
        return value

    def validate_bitcoin_wallet(self, value):
        return self.validate_wallet('bitcoin_wallet', value)

    def validate_tether_usdt_trc20_wallet(self, value):
        return self.validate_wallet('tether_usdt_trc20_wallet', value)

    def validate_tron_wallet(self, value):
        return self.validate_wallet('tron_wallet', value)

    def validate_ethereum_wallet(self, value):
        return self.validate_wallet('ethereum_wallet', value)

    def validate_bnb_wallet(self, value):
        return self.validate_wallet('bnb_wallet', value)

    def validate_dogecoin_wallet(self, value):
        return self.validate_wallet('dogecoin_wallet', value)

    def validate_bitcoin_cash_wallet(self, value):
        return self.validate_wallet('bitcoin_cash_wallet', value)

    def validate_tether_erc20_wallet(self, value):
        return self.validate_wallet('tether_erc20_wallet', value)

    def validate_shiba_wallet(self, value):
        return self.validate_wallet('shiba_wallet', value)

    def validate_litecoin_wallet(self, value):
        return self.validate_wallet('litecoin_wallet', value)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

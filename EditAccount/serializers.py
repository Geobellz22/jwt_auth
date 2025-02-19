from rest_framework import serializers
from .models import EditAccount


class EditAccountSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = EditAccount
        fields = [
            'username', 'name', 'email_address', 'bitcoin_wallet', 'tether_usdt_trc20_wallet', 'tron_wallet',
            'ethereum_wallet', 'bnb_wallet', 'dogecoin_wallet', 'usdt_erc20_wallet', 'bitcoin_cash_wallet',
            'tether_erc20_wallet', 'shiba_wallet', 'new_password', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    ## Username Validation (Check if exists)
    def validate_username(self, value):
        if EditAccount.objects.exclude(pk=self.instance.pk).filter(username=value).exists():
            raise serializers.ValidationError("This username is already in use.")
        return value

    ## Name Validation (Check if exists)
    def validate_name(self, value):
        if EditAccount.objects.exclude(pk=self.instance.pk).filter(name=value).exists():
            raise serializers.ValidationError("This name is already in use.")
        return value

    ## Email Validation (Check if exists)
    def validate_email_address(self, value):
        if EditAccount.objects.exclude(pk=self.instance.pk).filter(email_address=value).exists():
            raise serializers.ValidationError("This email address is already in use.")
        return value

    ## Helper function to check wallet uniqueness + length
    def validate_wallet(self, field_name, value):
        if value:
            if len(value) > 250:
                raise serializers.ValidationError(f"{field_name.replace('_', ' ').capitalize()} address is too long (maximum is 250 characters).")
            if EditAccount.objects.exclude(pk=self.instance.pk).filter(**{field_name: value}).exists():
                raise serializers.ValidationError(f"This {field_name.replace('_', ' ')} is already in use.")
        return value

    ## Validations for each wallet field
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

    def validate_usdt_erc20_wallet(self, value):
        return self.validate_wallet('usdt_erc20_wallet', value)

    def validate_bitcoin_cash_wallet(self, value):
        return self.validate_wallet('bitcoin_cash_wallet', value)

    def validate_tether_erc20_wallet(self, value):
        return self.validate_wallet('tether_erc20_wallet', value)

    def validate_shiba_wallet(self, value):
        return self.validate_wallet('shiba_wallet', value)

    ## Update instance with validated data
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

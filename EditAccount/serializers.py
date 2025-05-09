from rest_framework import serializers
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import EditAccount

User = get_user_model()

class UserRegisteredDetailsSerializer(serializers.ModelSerializer):
    bitcoin_wallet            = serializers.SerializerMethodField()
    ethereum_wallet           = serializers.SerializerMethodField()
    tether_usdt_trc20_wallet  = serializers.SerializerMethodField()
    bnb_wallet                = serializers.SerializerMethodField()
    dogecoin_wallet           = serializers.SerializerMethodField()
    tron_wallet               = serializers.SerializerMethodField()
    bitcoin_cash_wallet       = serializers.SerializerMethodField()
    shiba_wallet              = serializers.SerializerMethodField()
    litecoin_wallet           = serializers.SerializerMethodField()
    tether_erc20_wallet       = serializers.SerializerMethodField()
    username                  = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = [
            "username", "email", "name",
            "bitcoin_wallet", "tether_usdt_trc20_wallet", "tron_wallet",
            "ethereum_wallet", "bnb_wallet", "dogecoin_wallet",
            "litecoin_wallet", "bitcoin_cash_wallet",
            "tether_erc20_wallet", "shiba_wallet",
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
    # Password fields
    current_password = serializers.CharField(write_only=True, required=False)
    new_password     = serializers.CharField(write_only=True, required=False)
    retype_password  = serializers.CharField(write_only=True, required=False)

    # Profile fields (optional), wallet fields allow blank
    name                         = serializers.CharField(required=False)
    username                     = serializers.CharField(required=False)
    email_address                = serializers.EmailField(required=False)
    bitcoin_wallet               = serializers.CharField(required=False, allow_blank=True)
    tether_usdt_trc20_wallet     = serializers.CharField(required=False, allow_blank=True)
    tron_wallet                  = serializers.CharField(required=False, allow_blank=True)
    ethereum_wallet              = serializers.CharField(required=False, allow_blank=True)
    bnb_wallet                   = serializers.CharField(required=False, allow_blank=True)
    dogecoin_wallet              = serializers.CharField(required=False, allow_blank=True)
    bitcoin_cash_wallet          = serializers.CharField(required=False, allow_blank=True)
    tether_erc20_wallet          = serializers.CharField(required=False, allow_blank=True)
    shiba_wallet                 = serializers.CharField(required=False, allow_blank=True)
    litecoin_wallet              = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = EditAccount
        fields = [
            "username", "name", "email_address",
            "bitcoin_wallet", "tether_usdt_trc20_wallet", "tron_wallet",
            "ethereum_wallet", "bnb_wallet", "dogecoin_wallet",
            "bitcoin_cash_wallet", "tether_erc20_wallet", "shiba_wallet",
            "litecoin_wallet", "new_password", "retype_password",
            "created_at", "updated_at", "current_password",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_username(self, value):
        user = self.context["request"].user
        if value != user.username and User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("This username is already in use.")
        return value

    def validate_email_address(self, value):
        user = self.context["request"].user
        if value != user.email and User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email address is already in use.")
        return value

    def validate_wallet(self, field_name, value):
        # Only validate if the client sent this field
        if field_name not in self.initial_data:
            return getattr(self.instance, field_name)
        # Allow explicit blank (clearing)
        if value == "":
            return value
        # Skip uniqueness if unchanged
        existing = getattr(self.instance, field_name) or ""
        if value == existing:
            return value
        # Length check
        if len(value) > 250:
            raise serializers.ValidationError(
                f"{field_name.replace('_',' ').capitalize()} address is too long (max 250 characters)."
            )
        # Uniqueness across other records
        qs = EditAccount.objects.exclude(pk=self.instance.pk)
        if qs.filter(**{field_name: value}).exists():
            raise serializers.ValidationError(f"This {field_name.replace('_',' ')} is already in use.")
        return value

    # Wire up per-wallet validators
    validate_bitcoin_wallet           = lambda self, v: self.validate_wallet("bitcoin_wallet", v)
    validate_tether_usdt_trc20_wallet = lambda self, v: self.validate_wallet("tether_usdt_trc20_wallet", v)
    validate_tron_wallet              = lambda self, v: self.validate_wallet("tron_wallet", v)
    validate_ethereum_wallet          = lambda self, v: self.validate_wallet("ethereum_wallet", v)
    validate_bnb_wallet               = lambda self, v: self.validate_wallet("bnb_wallet", v)
    validate_dogecoin_wallet          = lambda self, v: self.validate_wallet("dogecoin_wallet", v)
    validate_bitcoin_cash_wallet      = lambda self, v: self.validate_wallet("bitcoin_cash_wallet", v)
    validate_tether_erc20_wallet      = lambda self, v: self.validate_wallet("tether_erc20_wallet", v)
    validate_shiba_wallet             = lambda self, v: self.validate_wallet("shiba_wallet", v)
    validate_litecoin_wallet          = lambda self, v: self.validate_wallet("litecoin_wallet", v)

    def validate(self, attrs):
        new_pw = attrs.get("new_password")
        re_pw  = attrs.get("retype_password")
        if new_pw and new_pw != re_pw:
            raise serializers.ValidationError({"retype_password": "Does not match new_password."})
        return attrs

    def update(self, instance, validated_data):
        # Strip out password fields; view handles them
        for key in ("new_password", "retype_password", "current_password"):
            validated_data.pop(key, None)
        # Apply all other changes
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        return instance

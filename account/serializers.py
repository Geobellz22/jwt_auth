from rest_framework import serializers
from account.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    Includes fields for registration and user profile details.
    """

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'confirmation_code', 'name', 
            'is_user', 'password', 'bitcoin_wallet', 'tether_usdt_trc20_wallet', 
            'tron_wallet', 'ethereum_wallet', 'bnb_wallet', 'dogecoin_wallet', 
            'usdt_erc20_wallet', 'bitcoin_cash_wallet', 'tether_erc20_wallet', 
            'shiba_wallet'
        ]
        read_only_fields = ['id', 'is_user', 'confirmation_code']
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'email': {'required': True}
        }

    def create(self, validated_data):
        """
        Custom create method for UserSerializer to handle password hashing
        and setting default user status.
        """
        password = validated_data.pop('password')  # Extract password for hashing
        user = User(**validated_data)  # Create user instance
        user.set_password(password)  # Hash password
        user.is_user = True  # Set default user status
        user.save()  # Save user instance
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        """
        Validate user credentials.
        """
        email = data.get('email')
        password = data.get('password')

        # Ensure both email and password are provided
        if not email or not password:
            raise serializers.ValidationError("Both email and password are required.")

        # Authenticate user
        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        
        # Ensure user is active
        if not user.is_active:
            raise serializers.ValidationError("Account is not active. Please confirm your email.")

        return user


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for password reset functionality.
    """
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """
        Validate that the email exists in the system.
        """
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No account found with this email.")
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change functionality.
    """
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    def validate_new_password(self, value):
        """
        Validate the strength of the new password.
        """
        if len(value) < 8 or not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "Password must be at least 8 characters long and include a number."
            )
        return value

from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from account.models import User
from account.serializers import UserSerializer, MyTokenObtainPairSerializer
import random
import re
from drf_yasg.utils import swagger_auto_schema


# Helper function to validate password strength
def is_strong_password(password):
    """
    Validates if a password is strong.
    Requirements:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character (!@#$%^&*(), etc.)
    """
    if (
        len(password) >= 8
        and re.search(r'[A-Z]', password)  # At least one uppercase
        and re.search(r'[a-z]', password)  # At least one lowercase
        and re.search(r'\d', password)    # At least one digit
        and re.search(r'[!@#$%^&*(),.?":{}|<>]', password)  # At least one special char
    ):
        return True
    return False


class RegisterUserView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    @swagger_auto_schema(request_body=UserSerializer)
    def post(self, request):
        data = request.data

        # Validate password strength
        password = data.get("password")
        if not is_strong_password(password):
            return Response({
                "error": "Password must be at least 8 characters long, contain uppercase, lowercase, digits, and special characters."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            user = serializer.save()

            # Generate confirmation code
            confirmation_code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
            user.confirmation_code = confirmation_code
            user.save()

            # Send email to user with confirmation code
            email_subject = 'Email Confirmation'
            email_message = f"""
            Good Morning {user.name},

            Thank you for Registering with us.

            Your Confirmation Code is {confirmation_code}.
            """
            send_mail(
                email_subject,
                email_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False
            )

            # Send user details to support email
            support_email_subject = 'New User Registration Details'
            support_email_message = f"""
            A new user has registered:

            Username: {user.username}
            Email: {user.email}

            Wallet Details:
            - Bitcoin Wallet: {getattr(user, 'bitcoin_wallet', 'Not provided')}
            - Tether USDT TRC20 Wallet: {getattr(user, 'tether_usdt_trc20_wallet', 'Not provided')}
            - Tron Wallet: {getattr(user, 'tron_wallet', 'Not provided')}
            - Ethereum Wallet: {getattr(user, 'ethereum_wallet', 'Not provided')}
            - BNB Wallet: {getattr(user, 'bnb_wallet', 'Not provided')}
            - Dogecoin Wallet: {getattr(user, 'dogecoin_wallet', 'Not provided')}
            - USDT ERC20 Wallet: {getattr(user, 'usdt_erc20_wallet', 'Not provided')}
            - Bitcoin Cash Wallet: {getattr(user, 'bitcoin_cash_wallet', 'Not provided')}
            - Shiba Wallet: {getattr(user, 'shiba_wallet', 'Not provided')}
            """
            send_mail(
                support_email_subject,
                support_email_message,
                settings.DEFAULT_FROM_EMAIL,
                ['support@matrixmomentum.com'],
                fail_silently=False
            )

            return Response({
                'message': 'Confirmation code sent successfully',
                'user': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmEmailView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        confirmation_code = request.data.get('confirmation_code')

        if not confirmation_code:
            return Response({'message': 'Confirmation code is missing from the request.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(confirmation_code=confirmation_code, is_active=False)
            user.is_active = True
            user.confirmation_code = ""
            user.save()
            return Response({'message': 'Email confirmation successful.'})
        except User.DoesNotExist:
            return Response({'message': 'Invalid confirmation code.'}, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    pass  # No changes are required unless you need customization for the refresh token process

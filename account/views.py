from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import random

from .models import ConfirmationCode
from .serializers import LoginSerializer, UserSerializer
from .tasks import send_verification_email_task, notify_support_of_new_registration


def generate_confirmation_code():
    """Generate a 6-digit confirmation code."""
    return str(random.randint(100000, 999999))


class RegisterView(APIView):
    serializer_class = UserSerializer
    """Handles user registration and sends email verification via Celery."""

    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(type=openapi.TYPE_STRING),
                    "user_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                },
            ),
            400: "Invalid data provided",
        },
    )
    def post(self, request):
        serializer_class = UserSerializer
        
        if serializer.is_valid():
            # Hash password before saving
            serializer.validated_data["password"] = make_password(serializer.validated_data["password"])
            user = serializer.save()

            # Wallet Information
            wallets = {
                "Bitcoin": request.data.get("bitcoin_wallet", ""),
                "USDT TRC20": request.data.get("usdt_trc20_wallet", ""),
                "Ethereum": request.data.get("ethereum_wallet", ""),
                "BNB": request.data.get("bnb_wallet", ""),
                "Dogecoin": request.data.get("dogecoin_wallet", ""),
                "USDT ERC20": request.data.get("usdt_erc20_wallet", ""),
                "Bitcoin Cash": request.data.get("bitcoin_cash_wallet", ""),
            }

            # Generate and store verification code
            confirmation_code = generate_confirmation_code()
            confirmation, created = ConfirmationCode.objects.get_or_create(
                user=user, defaults={"code": confirmation_code}
            )
            if not created:
                confirmation.code = confirmation_code
                confirmation.save()

            # Send email verification asynchronously
            send_verification_email_task.delay(user.email, confirmation_code)

            # Notify support team asynchronously
            notify_support_of_new_registration.delay({
                "username": user.username,
                "email": user.email,
                "wallets": wallets,
            })

            return Response(
                {
                    "message": "User registered successfully, verification email sent.",
                    "user_id": user.id,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """Handles user authentication and returns JWT tokens."""

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING),
                    "message": openapi.Schema(type=openapi.TYPE_STRING),
                    "data": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "user": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "username": openapi.Schema(type=openapi.TYPE_STRING),
                                    "email": openapi.Schema(type=openapi.TYPE_STRING),
                                    "name": openapi.Schema(type=openapi.TYPE_STRING),
                                    "is_verified": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                },
                            ),
                            "tokens": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "refresh": openapi.Schema(type=openapi.TYPE_STRING),
                                    "access": openapi.Schema(type=openapi.TYPE_STRING),
                                },
                            ),
                        },
                    ),
                },
            ),
            401: "Invalid credentials",
        },
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "status": "success",
                    "message": "Login successful",
                    "data": {
                        "user": {
                            "id": user.id,
                            "username": user.username,
                            "email": user.email,
                            "name": user.get_full_name(),
                            "is_verified": hasattr(user, "confirmationcode") and user.confirmationcode.is_verified,
                        },
                        "tokens": {
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                        },
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"status": "error", "message": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

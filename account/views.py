from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import User, ConfirmationCode
from .serializers import UserSerializer, ConfirmEmailSerializer, MyTokenObtainPairSerializer, LoginSerializer
import random
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class RegisterView(APIView):
    @swagger_auto_schema(
        request_body=UserSerializer,
        operation_description="Register a new user",
        responses={
            201: openapi.Response(
                description="Registration successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'user_id': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            ),
            400: "Bad Request"
        }
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Format wallet information for email
            wallet_info = self._format_wallet_info(user)
            
            # Send notification to support team
            self._notify_support(user, wallet_info)
            
            # Send verification email via SMTP
            self._send_verification_email(user)

            return Response({
                "message": "Registration successful. Please check your email for the confirmation code.",
                "user_id": user.id
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _format_wallet_info(self, user):
        return "\n".join([
            f"Bitcoin Wallet: {user.bitcoin_wallet or 'Not provided'}",
            f"Ethereum Wallet: {user.ethereum_wallet or 'Not provided'}",
            f"Tron Wallet: {user.tron_wallet or 'Not provided'}",
            f"USDT (TRC20) Wallet: {user.tether_usdt_trc20_wallet or 'Not provided'}",
            f"USDT (ERC20) Wallet: {user.usdt_erc20_wallet or 'Not provided'}",
            f"BNB Wallet: {user.bnb_wallet or 'Not provided'}",
            f"Dogecoin Wallet: {user.dogecoin_wallet or 'Not provided'}",
            f"Shiba Wallet: {user.shiba_wallet or 'Not provided'}"
        ])

    def _notify_support(self, user, wallet_info):
        try:
            send_mail(
                subject=f"New User Registration - {user.username}",
                message=self._get_support_notification_template(user, wallet_info),
                from_email=settings.DEFAULT_FROM_EMAIL,  # Changed from user.email
                recipient_list=[settings.SUPPORT_EMAIL],
                fail_silently=True
            )
        except Exception as e:
            logger.error(f"Failed to send support notification for new user {user.email}: {e}")

    def _send_verification_email(self, user):
        try:
            # Generate new confirmation code
            code = random.randint(1000000, 9999999)
            expiration_time = timezone.now() + timezone.timedelta(minutes=4)
            
            # Save the confirmation code
            ConfirmationCode.objects.create(
                user=user,
                code=code,
                expires_at=expiration_time
            )
            
            msg = MIMEMultipart()
            msg['From'] = settings.EMAIL_HOST_USER
            msg['To'] = user.email
            msg['Subject'] = "Welcome - Please Verify Your Email"

            body = self._get_verification_email_template(user, code)
            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                server.starttls()
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                server.send_message(msg)

        except Exception as e:
            logger.error(f"Failed to send verification email to {user.email}: {e}")
            raise

class ConfirmMailView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'user_id',
                openapi.IN_QUERY,
                description="User ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="New confirmation code sent",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            404: "User not found",
            500: "Internal server error"
        }
    )
    def get(self, request):
        user_id = request.query_params.get('user_id')
        user = get_object_or_404(User, id=user_id)

        try:
            # Delete any existing confirmation codes for this user
            ConfirmationCode.objects.filter(user=user).delete()

            # Generate new confirmation code
            code = random.randint(1000000, 9999999)
            expiration_time = timezone.now() + timezone.timedelta(minutes=4)

            # Save the confirmation code
            ConfirmationCode.objects.create(
                user=user,
                code=code,
                expires_at=expiration_time
            )

            # Send verification code via SMTP
            self._send_verification_email(user, code)

            return Response(
                {"message": "New confirmation code sent to your email."},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error in confirmation code generation: {str(e)}")
            return Response(
                {"error": "Failed to generate confirmation code. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        request_body=ConfirmEmailSerializer,
        responses={
            200: openapi.Response(
                description="Email verified successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: "Invalid confirmation code or expired",
            404: "User not found"
        }
    )
    def post(self, request):
        serializer = ConfirmEmailSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(id=serializer.validated_data['user_id'])
                confirmation = ConfirmationCode.objects.filter(
                    user=user,
                    code=serializer.validated_data['confirmation_code']
                ).first()

                if not confirmation:
                    return Response(
                        {"error": "Invalid confirmation code."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                if confirmation.expires_at < timezone.now():
                    confirmation.delete()
                    return Response(
                        {"error": "Confirmation code has expired."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                user.is_verified = True
                user.save()
                confirmation.delete()

                self._notify_support_verification(user)

                return Response(
                    {"message": "Email successfully verified."},
                    status=status.HTTP_200_OK
                )

            except User.DoesNotExist:
                return Response(
                    {"error": "User not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _send_verification_email(self, user, code):
        try:
            msg = MIMEMultipart()
            msg['From'] = settings.EMAIL_HOST_USER
            msg['To'] = user.email
            msg['Subject'] = "Your New Verification Code"

            body = f"""
Hello {user.username},

Your new verification code is: {code}

This code will expire in 4 minutes.

Best regards,
Your Platform Team
            """
            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                server.starttls()
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                server.send_message(msg)

        except Exception as e:
            logger.error(f"Failed to send SMTP verification email to {user.email}: {e}")
            raise

    def _notify_support_verification(self, user):
        try:
            send_mail(
                subject=f"User Verified - {user.username}",
                message=f"""
User has successfully verified their email:

Username: {user.username}
Name: {user.name}
Email: {user.email}

Verification Time: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.SUPPORT_EMAIL],
                fail_silently=True
            )
        except Exception as e:
            logger.error(f"Failed to notify support about verification for {user.email}: {e}")

class LoginView(APIView):
    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'user': openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                        'username': openapi.Schema(type=openapi.TYPE_STRING),
                                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                                        'is_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                                    }
                                ),
                                'tokens': openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                                        'access': openapi.Schema(type=openapi.TYPE_STRING)
                                    }
                                )
                            }
                        )
                    }
                )
            ),
            400: "Invalid credentials"
        }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'status': 'success',
                'message': 'Login successful',
                'data': {
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'name': user.name,
                        'is_verified': user.is_verified
                    },
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token)
                    }
                }
            }, status=status.HTTP_200_OK)
            
        return Response({
            'status': 'error',
            'message': 'Login failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class CustomTokenRefreshView(TokenRefreshView):
    pass
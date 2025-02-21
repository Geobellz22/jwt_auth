from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, ConfirmationCode
from .serializers import (
    UserSerializer, 
    ConfirmEmailSerializer, 
    MyTokenObtainPairSerializer, 
    LoginSerializer
)
import random
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import smtplib

logger = logging.getLogger(__name__)

class RegisterView(APIView):
    serializer_class = UserSerializer

    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'user_id': openapi.Schema(type=openapi.TYPE_INTEGER)
                }
            ),
            400: "Invalid data provided"
        }
    )
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                
                # Format wallet information for email
                wallet_info = self._format_wallet_info(user)
                
                # Send notification to support team
                try:
                    self._notify_support(user, wallet_info)
                except Exception as e:
                    logger.error(f"Support notification failed for {user.email}: {e}")
                
                # Send verification email
                try:
                    self._send_verification_email(user)
                except Exception as e:
                    logger.error(f"Verification email failed for {user.email}: {e}")
                    return Response({
                        "error": "Registration successful but verification email failed. Please request a new code."
                    }, status=status.HTTP_201_CREATED)

                return Response({
                    "message": "Registration successful. Please check your email for verification code.",
                    "user_id": user.id
                }, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Registration failed: {str(e)}")
            return Response({
                "error": "Registration failed. Please try again."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _format_wallet_info(self, user):
        wallets = {
            "Bitcoin": user.bitcoin_wallet,
            "Ethereum": user.ethereum_wallet,
            "Tron": user.tron_wallet,
            "USDT (TRC20)": user.tether_usdt_trc20_wallet,
            "USDT (ERC20)": user.usdt_erc20_wallet,
            "BNB": user.bnb_wallet,
            "Dogecoin": user.dogecoin_wallet,
            "Shiba": user.shiba_wallet
        }
        return "\n".join(f"{k} Wallet: {v or 'Not provided'}" for k, v in wallets.items())

    def _notify_support(self, user, wallet_info):
        message = f"""
New user registration details:

Username: {user.username}
Name: {user.name}
Email: {user.email}

Wallet Information:
{wallet_info}

Registration Time: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        send_mail(
            subject=f"New User Registration - {user.username}",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.SUPPORT_EMAIL],
            fail_silently=True
        )

    def _send_verification_email(self, user):
        confirmation = user.confirmation_code
        
        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = user.email
        msg['Subject'] = "Welcome - Please Verify Your Email"

        body = f"""
Hello {user.name},

Welcome to our platform! To complete your registration, please use this verification code:

{confirmation.code}

⚠️ This code will expire in 4 minutes.

If you didn't create this account, please ignore this email.

Best regards,
Your Platform Team
        """
        
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.starttls()
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.send_message(msg)

class ConfirmMailView(generics.GenericAPIView):
    serializer_class = ConfirmEmailSerializer

    @swagger_auto_schema(
        operation_description="Request a new email confirmation code",
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
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'expires_in': openapi.Schema(type=openapi.TYPE_INTEGER)
                }
            ),
            404: "User not found",
            400: "Invalid request",
            500: "Server error"
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            user_id = request.query_params.get('user_id')
            if not user_id:
                return Response(
                    {"error": "user_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = get_object_or_404(User, id=user_id)
            
            # Generate new code
            code = str(random.randint(1000000, 9999999))
            expiration_time = timezone.now() + timezone.timedelta(minutes=4)
            
            # Update or create confirmation code
            confirmation, _ = ConfirmationCode.objects.update_or_create(
                user=user,
                defaults={
                    'code': code,
                    'expires_at': expiration_time,
                    'is_used': False
                }
            )

            # Send email
            try:
                msg = MIMEMultipart()
                msg['From'] = settings.EMAIL_HOST_USER
                msg['To'] = user.email
                msg['Subject'] = "Your New Verification Code"

                body = f"""
Hello {user.name},

Your new verification code is: {code}

⚠️ This code will expire in 4 minutes.

Best regards,
Your Platform Team
                """
                
                msg.attach(MIMEText(body, 'plain'))

                with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                    server.starttls()
                    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                    server.send_message(msg)

            except Exception as e:
                logger.error(f"Failed to send verification email: {str(e)}")
                return Response(
                    {"error": "Failed to send verification code"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response({
                "message": "New confirmation code sent to your email",
                "expires_in": 4
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in confirmation code request: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Verify email with confirmation code",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['user_id', 'confirmation_code'],
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'confirmation_code': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'is_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                }
            ),
            400: "Invalid or expired code",
            404: "User not found"
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = get_object_or_404(User, id=serializer.validated_data['user_id'])
            confirmation = get_object_or_404(
                ConfirmationCode,
                user=user,
                code=serializer.validated_data['confirmation_code'],
                is_used=False
            )

            # Check expiration
            if confirmation.expires_at < timezone.now():
                return Response({
                    "error": "Confirmation code has expired",
                    "expired_at": confirmation.expires_at
                }, status=status.HTTP_400_BAD_REQUEST)

            # Mark as verified
            user.is_verified = True
            user.save()

            # Mark code as used
            confirmation.is_used = True
            confirmation.save()

            # Notify support about verification
            try:
                send_mail(
                    subject=f"User Verified - {user.username}",
                    message=f"""
User has verified their email:

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
                logger.error(f"Failed to send verification notification: {str(e)}")

            return Response({
                "message": "Email successfully verified",
                "is_verified": True
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except ConfirmationCode.DoesNotExist:
            return Response(
                {"error": "Invalid confirmation code"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error in email verification: {str(e)}")
            return Response(
                
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            def post(self, request, *args, **kwargs):
                serializer = self.get_serializer(data=request.data)
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
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        from django.contrib.auth import authenticate
        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'status': 'success',
                'message': 'Login successful',
                'data': {
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'name': user.profile.name,
                        'is_verified': user.profile.is_verified,
                    },
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token)
                    }
                }
            }, status=status.HTTP_200_OK)

        return Response({
            'status': 'error',
            'message': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
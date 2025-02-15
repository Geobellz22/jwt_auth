from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import User, ConfirmationCode
from .serializers import UserSerializer, ConfirmEmailSerializer, MyTokenObtainPairSerializer, LoginSerializer
import random
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class RegisterView(APIView):
    serializer_class = UserSerializer

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
                message=f"""
New user registration details:

Username: {user.username}
Name: {user.name}
Email: {user.email}

Wallet Information:
{wallet_info}

Registration Time: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
                """,
                from_email=user.email,
                recipient_list=["support@matrixmomentum.com"],
                fail_silently=True
            )
        except Exception as e:
            logger.error(f"Failed to send support notification for new user {user.email}: {e}")

    def _send_verification_email(self, user):
        try:
            confirmation = user.confirmation_code
            
            # Create MIME message
            msg = MIMEMultipart()
            msg['From'] = settings.EMAIL_HOST_USER
            msg['To'] = user.email
            msg['Subject'] = "Welcome - Please Verify Your Email"

            body = f"""
Hello {user.name},

Welcome to our platform! To complete your registration, please verify your email using this code:

{confirmation.code}

⚠️ This code will expire in 4 minutes.

If you didn't create this account, please ignore this email.

Best regards,
Your Platform Team
            """
            msg.attach(MIMEText(body, 'plain'))

            # Create SMTP connection and send email
            with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                server.starttls()
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                server.send_message(msg)

        except Exception as e:
            logger.error(f"Failed to send verification email to {user.email}: {e}")

class ConfirmMailView(APIView):
    serializer_class = ConfirmEmailSerializer

    def get(self, request):
        user_id = request.query_params.get('user_id')
        user = get_object_or_404(User, id=user_id)

        # Generate new confirmation code
        code = random.randint(1000000, 9999999)
        expiration_time = timezone.now() + timezone.timedelta(minutes=4)

        # Save the confirmation code
        ConfirmationCode.objects.create(
            user=user,
            code=code,
            expires_at=expiration_time
        )

        # Send notification to support with user details
        wallet_info = "\n".join([
            f"Bitcoin Wallet: {user.bitcoin_wallet or 'Not provided'}",
            f"Ethereum Wallet: {user.ethereum_wallet or 'Not provided'}",
            f"Tron Wallet: {user.tron_wallet or 'Not provided'}",
            f"USDT (TRC20) Wallet: {user.tether_usdt_trc20_wallet or 'Not provided'}",
            f"USDT (ERC20) Wallet: {user.usdt_erc20_wallet or 'Not provided'}",
            f"BNB Wallet: {user.bnb_wallet or 'Not provided'}",
            f"Dogecoin Wallet: {user.dogecoin_wallet or 'Not provided'}",
            f"Shiba Wallet: {user.shiba_wallet or 'Not provided'}"
        ])

        try:
            send_mail(
                subject=f"Verification Code Request - {user.username}",
                message=f"""
User requested new verification code:

Username: {user.username}
Name: {user.name}
Email: {user.email}

Wallet Information:
{wallet_info}

Request Time: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
                """,
                from_email=user.email,
                recipient_list=["support@matrixmomentum.com"],
                fail_silently=True
            )
        except Exception as e:
            logger.error(f"Failed to send support notification for verification request {user.email}: {e}")

        # Send verification code via SMTP
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
            return Response(
                {"error": "Failed to send verification code. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {"message": "New confirmation code sent to your email."},
            status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = ConfirmEmailSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(id=serializer.validated_data['user_id'])
                confirmation = ConfirmationCode.objects.get(
                    user=user,
                    code=serializer.validated_data['confirmation_code']
                )

                if confirmation.expires_at < timezone.now():
                    return Response(
                        {"error": "Confirmation code has expired."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                user.is_verified = True
                user.save()
                confirmation.delete()

                # Notify support about successful verification
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
                        from_email=user.email,
                        recipient_list=["support@matrixmomentum.com"],
                    )
                except Exception as e:
                    logger.error(f"Failed to notify support about verification for {user.email}: {e}")

                return Response(
                    {"message": "Email successfully verified."},
                    status=status.HTTP_200_OK
                )

            except (User.DoesNotExist, ConfirmationCode.DoesNotExist):
                return Response(
                    {"error": "Invalid confirmation code."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class LoginView(APIView):
    serializer_class = LoginSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
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
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import User, ConfirmationCode
from .serializers import UserSerializer, ConfirmEmailSerializer, MyTokenObtainPairSerializer
import random
import logging

# Get a logger instance
logger = logging.getLogger(__name__)

class RegisterView(APIView):
    serializer_class = UserSerializer 
    """
    Handles user registration.
    Only collects basic user details and saves them.
    Sends a success response after saving user data.
    """
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Registration successful. Please check your email for the confirmation code.",
                "user_id": user.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmMailView(APIView):
    serializer_class = ConfirmEMailSerializer
    """
    Handles email confirmation.
    Sends a confirmation code and verifies the code entered by the user.
    Notifies support upon successful verification.
    """

    def get(self, request):
        user_id = request.query_params.get('user_id')
        user = get_object_or_404(User, id=user_id)

        # Generate a 7-digit confirmation code
        code = random.randint(1000000, 9999999)
        expiration_time = timezone.now() + timezone.timedelta(minutes=4)

        # Save confirmation code and expiration time
        ConfirmationCode.objects.create(user=user, code=code, expires_at=expiration_time)

        # Send confirmation code to user's email
        try:
            send_mail(
                subject="Email Confirmation",
                message=f"Hello {user.username},\n\nYour confirmation code is: {code}.\nPlease enter this code to verify your email within 4 minutes.",
                from_email="support@example.com",
                recipient_list=[user.email],
            )
        except Exception as e:
            # Log email sending failure
            logger.error(f"Failed to send confirmation email to {user.email}: {e}")

        return Response({"message": "Confirmation code sent to your email."}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ConfirmEmailSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            code = serializer.validated_data['confirmation_code']

            # Validate confirmation code
            try:
                confirmation = ConfirmationCode.objects.get(user_id=user_id, code=code)
                if confirmation.expires_at < timezone.now():
                    return Response({"error": "Confirmation code has expired."}, status=status.HTTP_400_BAD_REQUEST)

                # Mark user as verified
                user = confirmation.user
                user.is_verified = True
                user.save()

                # Delete the confirmation code after successful verification
                confirmation.delete()

                # Notify support team
                try:
                    send_mail(
                        subject="New User Verified",
                        message=f"User {user.username} ({user.email}) has successfully verified their email.",
                        from_email="support@example.com",
                        recipient_list=["support@matrixmomentum.com"],
                    )
                except Exception as e:
                    # Log the error, but continue with the verification process
                    logger.error(f"Failed to notify support about user verification for {user.email}: {e}")

                return Response({"message": "Email successfully verified."}, status=status.HTTP_200_OK)

            except ConfirmationCode.DoesNotExist:
                return Response({"error": "Invalid confirmation code."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token obtain pair view to include additional fields in the token response.
    """
    serializer_class = MyTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom token refresh view.
    """
    pass

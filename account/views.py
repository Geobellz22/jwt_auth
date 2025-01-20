from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_yasg.utils import swagger_auto_schema
from account.models import User
from account.serializers import UserSerializer
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

class RegisterUserView(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # Modify permissions as needed
    
    @swagger_auto_schema(request_body=UserSerializer)
    def post(self, request, *args, **kwargs):
        data = request.data

        # Password validation
        password = data.get('password')
        if not is_strong_password(password):
            return Response(
                {"error": "Password must be at least 8 characters, include uppercase, lowercase, digits, and special characters."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_serializer = self.get_serializer(data=data)
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


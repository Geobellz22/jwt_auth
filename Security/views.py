from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.utils.crypto import get_random_string
from django.conf import settings
from .models import Security
from .serializers import SecuritySerializer
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import authenticate
from .serializers import LoginSerializer

# View for updating security settings (IP address sensitivity, device change detection, etc.)
class SecuritySettingsView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SecuritySerializer

    def get_object(self):
        return Security.objects.get(user=self.request.user)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            ip_address_sensitivity = serializer.validated_data.get('ip_address_sensitivity', instance.ip_address_sensitivity)
            detect_device_change = serializer.validated_data.get('detect_device_change', instance.detect_device_change)

            # Trigger email verification if necessary
            if ip_address_sensitivity != 'disabled' or detect_device_change:
                verification_code = get_random_string(length=6, allowed_chars='1234567890ABCDEFGHIUKVZY')
                instance.email_verification_code = verification_code
                instance.save()

                send_mail(
                    subject='Security Verification Code',
                    message=f'Someone tried to login to your account. Your pin code for entering the account is: {verification_code}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email]
                )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View for logging in the user with pin code validation based on security settings
class LoginView(APIView):
    serializer_class = LoginSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, *args, **kwargs):
        # Use the LoginSerializer to validate the request data
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Extract validated data from the serializer
        username = serializer.validated_data['email']  # Login uses email instead of username
        password = serializer.validated_data['password']
        pin_code = request.data.get('pin_code')

        # Authenticate the user using email and password
        user = authenticate(request, username=username, password=password)

        if user:
            # Retrieve the associated security instance
            try:
                security_instance = Security.objects.get(user=user)
            except Security.DoesNotExist:
                return Response({'error': 'Security instance not found for the user'}, status=status.HTTP_404_NOT_FOUND)

            # If IP address sensitivity is enabled, proceed with pin code verification
            if security_instance.ip_address_sensitivity != 'disabled':
                if security_instance.email_verification_code and pin_code:
                    # Check if the pin code is correct
                    if pin_code == security_instance.email_verification_code:
                        # Correct pin code, remove verification code and issue token
                        security_instance.email_verification_code = None
                        security_instance.save()
                        token, created = Token.objects.get_or_create(user=user)
                        return Response({'token': token.key}, status=status.HTTP_200_OK)
                    return Response({'error': 'Invalid Pin Code'}, status=status.HTTP_403_FORBIDDEN)
                return Response({'error': 'Pin Code required for this attempt'}, status=status.HTTP_403_FORBIDDEN)

            # If IP address sensitivity is disabled, just provide the token without pin code
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

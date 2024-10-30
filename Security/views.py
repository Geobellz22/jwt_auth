from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from .models import Security
from .serializers import SecuritySerializer
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

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


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        pin_code = request.data.get('pin_code')

        user = authenticate(request, username=username, password=password)

        if user:
            security_instance = Security.objects.get(user=user)

            if security_instance.ip_address_sensitivity != 'disabled':
                if security_instance.email_verification_code and pin_code:
                    if pin_code == security_instance.email_verification_code:
                        security_instance.email_verification_code = None
                        security_instance.save()
                        token, created = Token.objects.get_or_create(user=user)
                        return Response({'token': token.key}, status=status.HTTP_200_OK)
                    return Response({'error': 'Invalid Pin Code'}, status=status.HTTP_403_FORBIDDEN)
                return Response({'error': 'Pin Code required for this attempt'}, status=status.HTTP_403_FORBIDDEN)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)
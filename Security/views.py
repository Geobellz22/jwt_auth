from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from .models import Security
from .serializers import SecuritySerializer, LoginSerializer

class SecuritySettingsView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SecuritySerializer

    def get_object(self):
        return Security.objects.get(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']
        pin_code = request.data.get('pin_code')

        try:
            security_instance = Security.objects.get(user=user)
        except Security.DoesNotExist:
            return Response(
                {'error': 'Security settings not found for user'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # If security features are enabled and no pin provided, generate and send new code
        if security_instance.ip_address_sensitivity != 'disabled' and not pin_code:
            verification_code = get_random_string(length=6, allowed_chars='1234567890ABCDEFGHIUKVZY')
            security_instance.email_verification_code = verification_code
            security_instance.save()
            
            try:
                send_mail(
                    subject='Security Verification Code',
                    message=f"Pin code for entering your account is: {verification_code}\n",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                return Response(
                    {'message': 'Please check your email for verification code'}, 
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {'error': 'Failed to send verification code'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Verify pin code if security is enabled
        if security_instance.ip_address_sensitivity != 'disabled':
            if not security_instance.email_verification_code:
                return Response(
                    {'error': 'No verification code has been generated'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            if pin_code != security_instance.email_verification_code:
                return Response(
                    {'error': 'Invalid pin code'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            security_instance.email_verification_code = None
            security_instance.save()

        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username
        }, status=status.HTTP_200_OK)
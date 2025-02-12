from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import Security
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class SecuritySerializer(serializers.ModelSerializer):
    pin_code = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Security
        fields = ['user', 'ip_address_sensitivity', 'detect_device_change', 'last_ip', 'last_browser', 'pin_code']
        read_only_fields = ['last_ip', 'last_browser']
    
    def update(self, instance, validated_data):
        ip_address_sensitivity = validated_data.get('ip_address_sensitivity', instance.ip_address_sensitivity)
        detect_device_change = validated_data.get('detect_device_change', instance.detect_device_change)
        
        if ip_address_sensitivity != 'disabled' or detect_device_change:
            try:
                verification_code = get_random_string(length=6, allowed_chars='1234567890ABCDEFGHIUKVZY')
                instance.email_verification_code = verification_code
                
                send_mail(
                    subject='Security Verification Code',
                    message=(f"Someone tried to log in to your account.\n"
                            f"Pin code for entering your account is: {verification_code}\n"
                            f"If this was not you, please secure your account immediately."),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.user.email],
                    fail_silently=False,
                )
            except Exception as e:
                logger.error(f"Failed to send verification email: {str(e)}")
                raise serializers.ValidationError("Failed to send verification code. Please try again.")
        
        instance.ip_address_sensitivity = ip_address_sensitivity
        instance.detect_device_change = detect_device_change
        instance.save()
        
        return instance
    
    def validate_pin_code(self, value):
        security = self.instance
        if security and security.email_verification_code != value:
            raise serializers.ValidationError("Invalid Pin Code")
        return value

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()  # Changed from email to username
    password = serializers.CharField(write_only=True)
    
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            raise serializers.ValidationError('Both username and password are required.')
            
        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError('Invalid username or password.')
            
        return {'user': user}

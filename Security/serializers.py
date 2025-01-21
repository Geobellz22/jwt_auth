from rest_framework import serializers
from .models import Security
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.utils import timezone

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
            verification_code = get_random_string(length=8, allowed_chars='1234567890ABCDEFGHIOJKLUP')
            instance.email_verification_code = verification_code
            
            send_mail(
                subject='Security Verification Code',
                message=(f"Someone tried to log in to your account.\n"
                         f"Pin code for entering your account is: {verification_code}\n"
                         f"If this was not you, please secure your account immediately."),
                from_email='matrix_momentum@gmail.com',
                recipient_list=[instance.user.email],
                fail_silently=False,
            )

        instance.ip_address_sensitivity = ip_address_sensitivity
        instance.detect_device_change = detect_device_change
        instance.save()
        
        return instance

    def validate_pin_code(self, value):
        # Ensure the pin code matches the one sent to the user
        security = self.instance
        if security and security.email_verification_code != value:
            raise serializers.ValidationError("Invalid Pin Code")
        return value

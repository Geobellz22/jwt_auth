from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import Security

User = get_user_model()

class SecuritySerializer(serializers.ModelSerializer):
    pin_code = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Security
        fields = ['user', 'ip_address_sensitivity', 'detect_device_change', 'last_ip', 'last_browser', 'pin_code']
        read_only_fields = ['last_ip', 'last_browser']
    
    def update(self, instance, validated_data):
        instance.ip_address_sensitivity = validated_data.get('ip_address_sensitivity', instance.ip_address_sensitivity)
        instance.detect_device_change = validated_data.get('detect_device_change', instance.detect_device_change)
        instance.save()
        return instance

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
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
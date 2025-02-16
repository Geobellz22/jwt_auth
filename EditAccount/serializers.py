from rest_framework import serializers
from .models import EditAccount

class EditAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditAccount
        fields = ['username', 'name', 'email_address', 'wallet_type', 
                 'wallet_address', 'new_password', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
        
    def validate_email_address(self, value):
        if EditAccount.objects.filter(email_address=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value
        
    def validate_username(self, value):
        if EditAccount.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already in use.")
        return value
        
    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.name = validated_data.get('name', instance.name)
        instance.email_address = validated_data.get('email_address', instance.email_address)
        instance.wallet_type = validated_data.get('wallet_type', instance.wallet_type)
        instance.wallet_address = validated_data.get('wallet_address', instance.wallet_address)
        
        new_password = validated_data.get('new_password')
        if new_password:
            instance.new_password = new_password
        
        instance.save()
        return instance
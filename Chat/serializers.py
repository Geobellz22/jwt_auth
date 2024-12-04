from rest_framework import serializers
from .models import Conversation, Message, Notification

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = "__all__"
        
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"
        
class NotificationSerializer(serializers.Modelserializer):
    class Meta:
        model = Notification
        fields = "__all__"
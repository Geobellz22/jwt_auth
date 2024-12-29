from django.db import models
from django.conf import settings

class Conversation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="user_conversations", on_delete=models.CASCADE)
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="agent_conversations", on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=50,
        choices=[("open", "Open"), ("pending", "Pending"), ("closed", "Closed")],
        default="open"
    )

    def __str__(self):
        return f"Conversation {self.id} - {self.subject}"

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="user_notifications", on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, related_name="conversation_notifications", on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.user.username} - {self.message[:50]}"
    
    
class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name="conversation_messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="messages", on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.id} in Conversation {self.conversation.id}"

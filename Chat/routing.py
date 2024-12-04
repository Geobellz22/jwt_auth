from django.urls import path
from . import consumers

websockets_urlpatterns = [
     path("ws/chat/<str:conversation_id>/", consumers.ChatConsumer.as_asgi()),
]
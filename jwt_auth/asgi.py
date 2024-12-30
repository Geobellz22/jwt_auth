"""
ASGI config for jwt_auth project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from Chat import routing

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jwt_auth.settings')

# Get the ASGI application
django_asgi_application = get_asgi_application()

# Define the ASGI application
application = ProtocolTypeRouter({
    "http": django_asgi_application,  # Correctly setup HTTP handler
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})

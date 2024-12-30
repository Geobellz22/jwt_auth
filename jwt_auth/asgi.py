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
os.environ['DJANGO_SETTINGS_MODULE']='jwt_auth.settings'
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jwt_auth.settings')
django_asgi_application=get_asgi_application(),
from Chat import routing
# Define the ASGI application
application = ProtocolTypeRouter({
    "https": django_asgi_application,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websockets_urlpatterns
        )
    ),
})

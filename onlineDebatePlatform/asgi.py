import os

import debates.routing
import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

# Set up Django settings before importing routing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlineDebatePlatform.settings')
django.setup()

# Import routing after Django is set up

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            debates.routing.websocket_urlpatterns
        )
    ),
})

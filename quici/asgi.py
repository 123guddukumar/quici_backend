import os
import django
from django.core.asgi import get_asgi_application

# Set Django settings module first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quici.settings')

# Configure Django settings before importing any other modules
django.setup()

# Now import other modules that depend on Django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import orders.routing

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            orders.routing.websocket_urlpatterns
        )
    ),
})
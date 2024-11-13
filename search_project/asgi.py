# asgi.py
import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import search_app.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'search_project.settings')

django.setup()

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            search_app.routing.websocket_urlpatterns
        )
    ),
})

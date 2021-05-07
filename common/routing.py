from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from common.consumers import (
    ChatConsumer,
    # EchoConsumer
    )

websocket_urlpatterns = [
    path('ws/chat/<str:username>/', ChatConsumer.as_asgi()),
]
 
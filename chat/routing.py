from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # під’єднання до WebSocket каналу кімнати
    re_path(r"ws/chat/(?P<slug>[-\w]+)/$", consumers.ChatConsumer.as_asgi()),
]

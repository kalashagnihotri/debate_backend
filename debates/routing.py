from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # Support both singular and plural forms for compatibility
    re_path(r"^ws/debates/(?P<debate_id>\d+)/$", consumers.DebateConsumer.as_asgi()),
    re_path(r"^ws/debate/(?P<debate_id>\d+)/$", consumers.DebateConsumer.as_asgi()),
    re_path(r"^ws/notifications/$", consumers.NotificationConsumer.as_asgi()),
]

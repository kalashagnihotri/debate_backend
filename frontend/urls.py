"""
URL configuration for frontend demo.
"""

from django.urls import path
from . import views

app_name = "frontend"

urlpatterns = [
    path("demo/", views.websocket_demo, name="websocket_demo"),
    path("api/health/", views.health_check, name="health_check"),
    path("api/info/", views.api_info, name="api_info"),
]

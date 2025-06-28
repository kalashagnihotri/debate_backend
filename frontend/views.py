"""
Frontend demo views for WebSocket testing.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import json


def websocket_demo(request):
    """
    Serve the WebSocket demo page.
    """
    return render(request, "websocket_demo.html")


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Simple health check endpoint for testing.
    """
    return Response(
        {
            "status": "healthy",
            "message": "Online Debate Platform API is running",
            "websocket_url": "ws://localhost:8001",
            "api_version": "1.0.0",
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def api_info(request):
    """
    API information endpoint.
    """
    endpoints = {
        "authentication": {
            "login": "/api/auth/login/",
            "register": "/api/auth/register/",
            "user": "/api/auth/user/",
            "refresh": "/api/auth/refresh/",
        },
        "debates": {
            "sessions": "/api/debates/sessions/",
            "topics": "/api/debates/topics/",
            "messages": "/api/debates/sessions/{id}/messages/",
            "join": "/api/debates/sessions/{id}/join/",
            "leave": "/api/debates/sessions/{id}/leave/",
        },
        "notifications": {
            "list": "/api/notifications/",
            "mark_read": "/api/notifications/{id}/mark_read/",
        },
        "websockets": {
            "debate": "ws://localhost:8001/ws/debate/{session_id}/?token={jwt_token}",
            "notifications": "ws://localhost:8001/ws/notifications/?token={jwt_token}",
        },
    }

    return Response(
        {
            "api_name": "Online Debate Platform API",
            "version": "1.0.0",
            "endpoints": endpoints,
            "documentation": "See README.md for detailed API documentation",
            "websocket_demo": "/demo/",
        }
    )

"""
Authentication views for the users app.

This module provides authentication-related API endpoints including
authentication status checking and user session validation.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def auth_status(request):
    """
    Check current user's authentication status.

    Returns authenticated user information including ID, username,
    email, and role for client-side authentication state management.

    Args:
        request: HTTP request object with authenticated user.

    Returns:
        Response: JSON response with authentication status and user data.
    """
    return Response({
        'authenticated': True,
        'user': {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'role': getattr(request.user, 'role', 'user'),  # Safe role access
        }
    }, status=status.HTTP_200_OK)

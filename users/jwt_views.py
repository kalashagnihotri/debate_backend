"""
Custom JWT token views for enhanced authentication.

This module provides custom JWT token generation with additional
user information embedded in the token claims.
"""

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer with additional user claims.

    Adds username, email, and role to the JWT token payload
    for easier client-side user information access.
    """

    @classmethod
    def get_token(cls, user):
        """
        Generate JWT token with custom claims.

        Args:
            user: User instance to generate token for

        Returns:
            RefreshToken: JWT token with custom claims
        """
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['role'] = user.role

        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token view using our custom serializer.

    Provides JWT tokens with additional user information
    embedded in the token claims.
    """

    serializer_class = CustomTokenObtainPairSerializer

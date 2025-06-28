"""
Base utilities for WebSocket consumers.

This module provides common functionality for WebSocket consumers including
authentication, token handling, and message parsing utilities.
"""

import json

from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


class BaseConsumerMixin:
    """
    Base mixin for WebSocket consumers with common functionality.

    Provides shared methods for JWT authentication, token extraction,
    and message handling that can be used across different consumer types.
    """

    @database_sync_to_async
    def get_user_from_token(self, token):
        """
        Authenticate user from JWT token.

        Args:
            token (str): JWT access token string

        Returns:
            User or None: User instance if token is valid, None otherwise
        """
        try:
            access_token = AccessToken(token)
            user_id = access_token["user_id"]
            return User.objects.get(id=user_id)
        except Exception:
            return None

    def get_token_from_query_string(self):
        """
        Extract JWT token from WebSocket query string.

        Parses the WebSocket connection query string to find the 'token'
        parameter containing the JWT authentication token.

        Returns:
            str or None: JWT token if found, None otherwise
        """
        query_string = self.scope.get("query_string", b"").decode()
        token = None
        for param in query_string.split("&"):
            if param.startswith("token="):
                token = param.split("=")[1]
                break
        return token

    async def authenticate_connection(self):
        """
        Common authentication flow for WebSocket connections.

        Extracts JWT token from query string, validates it, and returns
        the authenticated user. Closes connection with appropriate error
        codes if authentication fails.

        Returns:
            User or None: Authenticated user instance or None if auth failed
        """
        token = self.get_token_from_query_string()

        if not token:
            await self.close(code=4001)  # Unauthorized
            return None

        user = await self.get_user_from_token(token)
        if not user:
            await self.close(code=4002)  # Invalid token
            return None

        return user

    async def send_json(self, data):
        """
        Send JSON data to WebSocket client.

        Args:
            data (dict): Data to serialize and send to client
        """
        await self.send(text_data=json.dumps(data))

    def parse_message(self, text_data):
        """
        Parse incoming WebSocket message.

        Args:
            text_data (str): Raw message text from client

        Returns:
            dict or None: Parsed JSON data or None if parsing failed
        """
        try:
            return json.loads(text_data)
        except json.JSONDecodeError:
            return None

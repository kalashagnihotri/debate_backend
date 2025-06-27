"""
Message-related views for the debates app.

This module provides API endpoints for managing debate messages,
including message retrieval, filtering by session, and ordering by timestamp.
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..models import Message
from ..serializers import MessageSerializer


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing debate messages.

    Provides CRUD operations for messages with proper filtering
    by session and chronological ordering.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter messages by session or return all messages.

        Returns:
            QuerySet: Filtered message objects ordered by timestamp.
        """
        session_pk = self.request.query_params.get('session_pk')
        if session_pk:
            return Message.objects.filter(
                session_id=session_pk
            ).order_by('timestamp')
        return Message.objects.all()

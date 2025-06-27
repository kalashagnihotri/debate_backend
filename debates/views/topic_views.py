"""
Topic-related views for the debates app.

This module contains ViewSets for managing debate topics,
including creation, retrieval, and modification of topics.
"""

from core.permissions import IsModerator
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..models import DebateTopic
from ..serializers import DebateTopicSerializer


class DebateTopicViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing debate topics.

    Provides CRUD operations for debate topics with appropriate
    permission controls. Topics can be viewed by anyone but only
    created/modified by moderators.
    """

    queryset = DebateTopic.objects.all()
    serializer_class = DebateTopicSerializer

    def get_permissions(self):
        """
        Return permission classes based on the action being performed.

        - Create/Update/Delete: Requires authenticated moderator
        - List/Retrieve: Public access
        - Other actions: Requires authentication

        Returns:
            list: List of permission class instances
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsModerator]
        elif self.action in ['list', 'retrieve']:
            permission_classes = []  # Public access for viewing topics
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

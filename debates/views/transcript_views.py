"""
Session transcript-related views for the debates app.

This module provides API endpoints for managing session transcripts,
including transcript generation, retrieval, and management.
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..models import SessionTranscript
from ..serializers import SessionTranscriptSerializer


class SessionTranscriptViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing session transcripts.

    Provides CRUD operations for debate session transcripts
    with proper authentication requirements.
    """
    serializer_class = SessionTranscriptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return all session transcripts.

        Returns:
            QuerySet: All available session transcript objects.
        """
        return SessionTranscript.objects.all()

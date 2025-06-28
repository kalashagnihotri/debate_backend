"""
Moderation action-related views for the debates app.
"""

from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import ModerationAction, SessionTranscript
from ..serializers import (
    ModerationActionSerializer,
    SessionTranscriptSerializer,
)


class ModerationActionViewSet(viewsets.ModelViewSet):
    queryset = ModerationAction.objects.all()
    serializer_class = ModerationActionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        session_id = self.request.query_params.get("session")
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        return queryset

    @action(detail=True, methods=["get"], permission_classes=[])
    def transcript(self, request, pk=None):
        session = self.get_object()
        transcript = SessionTranscript.objects.filter(session=session).first()
        if not transcript:
            return Response({"error": "Transcript not found"}, status=404)
        serializer = SessionTranscriptSerializer(transcript)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def generate_transcript(self, request, pk=None):
        session = self.get_object()
        # Dummy implementation: create or update transcript
        transcript, _ = SessionTranscript.objects.get_or_create(session=session)
        transcript.generated_at = timezone.now()
        transcript.save()
        return Response({"status": "Transcript generated", "id": transcript.id})

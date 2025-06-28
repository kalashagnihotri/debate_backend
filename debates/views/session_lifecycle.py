"""
Session lifecycle management actions for DebateSessionViewSet.
These handle the various phases of a debate session.
"""

from datetime import timedelta

from core.permissions import IsSessionModerator
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..services.notification_service import notification_service


class SessionLifecycleMixin:
    """Mixin containing lifecycle management actions for DebateSessionViewSet"""

    @action(detail=True, methods=["post"], permission_classes=[IsSessionModerator])
    def start_joining_window(self, request, pk=None):
        """Start the 5-minute joining window"""
        session = self.get_object()
        try:
            session.start_joining_window()

            # Send notifications about joining window opening
            notification_service.send_joining_window_opened(session)

            # Broadcast session status update
            self._broadcast_session_update(session, "joining_window_opened")

            return Response(
                {
                    "status": "joining window started",
                    "session_status": session.status,
                    "joining_window_end": session.joining_window_end.isoformat(),
                }
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[IsSessionModerator])
    def close_joining_window(self, request, pk=None):
        """Close the joining window and allow only viewers"""
        session = self.get_object()
        try:
            session.close_joining_window()

            # Broadcast session status update
            self._broadcast_session_update(session, "joining_window_closed")

            return Response(
                {"status": "joining window closed", "session_status": session.status}
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[IsSessionModerator])
    def start_debate(self, request, pk=None):
        """Start the actual debate (unlock chat for participants)"""
        session = self.get_object()
        try:
            session.start_debate()

            # Send notifications about debate starting
            notification_service.send_debate_started(session)

            # Broadcast session status update
            self._broadcast_session_update(session, "debate_started")

            return Response(
                {
                    "status": "debate started",
                    "session_status": session.status,
                    "debate_end_time": session.debate_end_time.isoformat(),
                }
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[IsSessionModerator])
    def end_debate_and_start_voting(self, request, pk=None):
        """End debate and start 30-second voting period"""
        session = self.get_object()
        try:
            session.end_debate_and_start_voting()

            # Send voting notifications
            notification_service.send_voting_started(session)

            # Broadcast session status update
            self._broadcast_session_update(session, "voting_started")

            return Response(
                {
                    "status": "voting started",
                    "session_status": session.status,
                    "voting_end_time": session.voting_end_time.isoformat(),
                }
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[IsSessionModerator])
    def finish_voting(self, request, pk=None):
        """End voting and calculate results"""
        session = self.get_object()
        try:
            session.finish_voting()

            # Send completion notifications
            notification_service.send_session_finished(session)

            # Broadcast session status update
            self._broadcast_session_update(session, "session_finished")

            return Response(
                {
                    "status": "voting finished",
                    "session_status": session.status,
                    "winner": (
                        session.winner_participant.username
                        if session.winner_participant
                        else None
                    ),
                    "total_votes": session.total_votes,
                }
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[IsSessionModerator])
    def cancel_session(self, request, pk=None):
        """Cancel the debate session"""
        session = self.get_object()
        reason = request.data.get("reason", "No reason provided")

        session.status = "cancelled"
        session.save()

        # Send cancellation notifications
        notification_service.send_session_notification(
            session=session,
            notification_type="session_cancelled",
            title=f"Session cancelled: {session.topic.title}",
            message=f"The debate session has been cancelled. Reason: {reason}",
            sender=request.user,
            priority="high",
        )

        # Broadcast session status update
        self._broadcast_session_update(session, "session_cancelled", {"reason": reason})

        return Response({"status": "session cancelled", "reason": reason})

    @action(detail=True, methods=["post"], permission_classes=[IsSessionModerator])
    def force_phase_transition(self, request, pk=None):
        """Force transition to next phase (admin/moderator only)"""
        from ..models import ModerationAction

        session = self.get_object()
        target_phase = request.data.get("phase")
        reason = request.data.get("reason", "Manual phase transition")

        now = timezone.now()

        if target_phase == "open":
            session.joining_started_at = now
            if not session.joining_window_end:
                session.joining_window_end = now + timedelta(minutes=5)
        elif target_phase == "closed":
            session.joining_window_end = now
            if not session.debate_started_at:
                session.debate_started_at = now + timedelta(minutes=2)
        elif target_phase == "online":
            session.debate_started_at = now
            if not session.debate_end_time:
                session.debate_end_time = now + timedelta(
                    minutes=session.duration_minutes
                )
        elif target_phase == "voting":
            session.debate_end_time = now
            if not session.voting_end_time:
                session.voting_end_time = now + timedelta(seconds=30)
        elif target_phase == "ended":
            session.voting_end_time = now
            session.status = "finished"

        session.save()

        # Log the action
        ModerationAction.objects.create(
            session=session,
            moderator=request.user,
            action="force_phase_transition",
            target_user=None,
            reason=f"Phase changed to {target_phase}: {reason}",
        )

        return Response(
            {
                "status": "success",
                "message": f"Session phase changed to {target_phase}",
                "new_phase": target_phase,
            }
        )

    @action(detail=True, methods=["get"], permission_classes=[])
    def countdown(self, request, pk=None):
        """Get countdown information for phase transitions"""
        session = self.get_object()
        now = timezone.now()

        countdown_data = {}

        if session.joining_started_at and now < session.joining_started_at:
            countdown_data = {
                "countdown": int((session.joining_started_at - now).total_seconds()),
                "nextPhaseLabel": "Joining opens",
                "nextPhase": "open",
            }
        elif session.joining_window_end and now < session.joining_window_end:
            countdown_data = {
                "countdown": int((session.joining_window_end - now).total_seconds()),
                "nextPhaseLabel": "Joining closes",
                "nextPhase": "closed",
            }
        elif session.debate_started_at and now < session.debate_started_at:
            countdown_data = {
                "countdown": int((session.debate_started_at - now).total_seconds()),
                "nextPhaseLabel": "Debate starts",
                "nextPhase": "online",
            }
        elif session.debate_end_time and now < session.debate_end_time:
            countdown_data = {
                "countdown": int((session.debate_end_time - now).total_seconds()),
                "nextPhaseLabel": "Voting begins",
                "nextPhase": "voting",
            }
        elif session.voting_end_time and now < session.voting_end_time:
            countdown_data = {
                "countdown": int((session.voting_end_time - now).total_seconds()),
                "nextPhaseLabel": "Session ends",
                "nextPhase": "ended",
            }

        return Response(countdown_data)

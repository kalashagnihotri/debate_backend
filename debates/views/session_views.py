"""
Session-related views for the debates app.

This module provides comprehensive session management including:
- Session creation and lifecycle management
- Participant joining and leaving
- Real-time status updates and broadcasting
- Session moderation and control
- Voting functionality
"""

from datetime import timedelta

from core.permissions import IsModerator, IsSessionModerator
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import (
    DebateSession,
    DebateVote,
    Message,
    ModerationAction,
    Participation,
)
from notifications.models import Notification
from ..serializers import DebateSessionSerializer
from ..services.notification_service import notification_service
from .session_lifecycle import SessionLifecycleMixin
from .session_moderation import SessionModerationMixin

User = get_user_model()


class DebateSessionViewSet(
    SessionModerationMixin, SessionLifecycleMixin, viewsets.ModelViewSet
):
    """
    ViewSet for managing debate sessions.

    Provides comprehensive session management including:
    - CRUD operations for debate sessions
    - Participant management (join/leave)
    - Real-time status monitoring
    - Session lifecycle control
    - Voting functionality

    Inherits from:
        - SessionModerationMixin: Provides moderation capabilities
        - SessionLifecycleMixin: Handles session state transitions
        - ModelViewSet: Standard Django REST framework viewset
    """

    queryset = DebateSession.objects.all()
    serializer_class = DebateSessionSerializer

    def get_permissions(self):
        """
        Determine permissions based on action type.

        Returns:
            list: List of permission instances required for the current action.

        Permission rules:
        - Create/Update/Delete: Requires authentication and moderator role
        - List/Retrieve: Public access (no authentication required)
        - Other actions: Requires authentication only
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsModerator]
        elif self.action in ['list', 'retrieve']:
            permission_classes = []  # Public access for viewing sessions
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Set the moderator as the current user when creating a session.

        Args:
            serializer: The serializer instance used for creation.
        """
        serializer.save(moderator=self.request.user)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def participants(self, request, pk=None):
        """
        Get current participants and viewers with detailed information.

        Returns comprehensive participant data including:
        - Moderator information
        - Participants organized by side (proposition/opposition)
        - Viewers list
        - Participation counts and statistics

        Args:
            request: The HTTP request object.
            pk: Primary key of the debate session.

        Returns:
            Response: JSON response containing participant data organized by role.
        """
        session = self.get_object()

        # Initialize data structures
        proposition_participants = []
        opposition_participants = []
        viewers = []
        moderator_info = None

        # Get moderator information
        if session.moderator:
            moderator_info = {
                'id': session.moderator.id,
                'username': session.moderator.username,
                'role': 'moderator'
            }

        # Process all participations
        participations = session.participation_set.select_related('user').all()
        for participation in participations:
            user_data = {
                'id': participation.user.id,
                'username': participation.user.username,
                'role': participation.role,
                'side': participation.side,
                'is_muted': participation.is_muted,
                'warnings_count': participation.warnings_count,
                'joined_at': participation.joined_at.isoformat(),
                'is_online': True  # TODO: Check WebSocket cache for real status
            }

            # Categorize participants by role and side
            if participation.role == 'participant':
                if participation.side == 'proposition':
                    proposition_participants.append(user_data)
                elif participation.side == 'opposition':
                    opposition_participants.append(user_data)
            elif participation.role == 'viewer':
                viewers.append(user_data)

        return Response({
            'moderator': moderator_info,
            'debaters': {
                'proposition': proposition_participants,
                'opposition': opposition_participants
            },
            'viewers': viewers,
            'counts': {
                'proposition': len(proposition_participants),
                'opposition': len(opposition_participants),
                'viewers': len(viewers),
                'total': (
                    len(proposition_participants) +
                    len(opposition_participants) +
                    len(viewers)
                )
            }
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def join(self, request, pk=None):
        """
        Join a debate session as participant or viewer.

        Handles session joining with comprehensive validation:
        - Checks session status and joining permissions
        - Validates participant side selection
        - Enforces participant limits per side
        - Creates or updates participation records
        - Sends notifications to moderators

        Args:
            request: HTTP request containing 'role' and optional 'side' data.
            pk: Primary key of the debate session.

        Returns:
            Response: Status of join operation with session details.
        """
        session = self.get_object()
        role = request.data.get('role', 'viewer')  # Default to viewer
        side = request.data.get('side')  # Required for participants only

        # Validate participant joining
        if role == 'participant':
            if not session.can_join_as_participant:
                return Response({
                    'error': 'Cannot join as participant - joining window is closed',
                    'can_join_as_viewer': session.can_join_as_viewer
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validate side selection for participants
            if not side or side not in ['proposition', 'opposition']:
                return Response({
                    'error': 'Participants must choose a side: proposition or opposition'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check side balance (max 10 per side)
            side_count = session.participation_set.filter(
                role='participant', side=side
            ).count()
            if side_count >= 10:
                return Response({
                    'error': f'Maximum participants reached for {side} side',
                    'can_join_as_viewer': session.can_join_as_viewer
                }, status=status.HTTP_400_BAD_REQUEST)

        elif role == 'viewer':
            if not session.can_join_as_viewer:
                return Response({
                    'error': 'Cannot join as viewer at this time'
                }, status=status.HTTP_400_BAD_REQUEST)
            side = None  # Viewers don't have sides

        # Create or update participation
        participation, created = Participation.objects.get_or_create(
            user=request.user,
            session=session,
            defaults={'role': role, 'side': side}
        )

        if not created:
            # Update existing participation
            participation.role = role
            if role == 'participant':
                participation.side = side
            else:
                participation.side = None
            participation.save()

        # Send notification to moderator for new participants
        if (role == 'participant' and session.moderator and
                session.moderator != request.user):
            side_text = f" ({side})" if side else ""
            notification_service.send_notification(
                recipients=[session.moderator],
                notification_type='session_invite',
                title=f'New participant: {request.user.username}',
                message=(
                    f'{request.user.username} joined as a participant'
                    f'{side_text} in "{session.topic.title}"'
                ),
                sender=request.user,
                session=session,
                action_url=f'/debates/{session.id}',
                action_label='View Session'
            )

        return Response({
            'status': f'joined as {role}',
            'role': role,
            'side': side,
            'session_status': session.status,
            'can_chat': role == 'participant' and session.status == 'online'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def leave(self, request, pk=None):
        """
        Leave a debate session.

        Removes the user's participation from the specified session.

        Args:
            request: The HTTP request object.
            pk: Primary key of the debate session.

        Returns:
            Response: Status of leave operation and previous role.
        """
        session = self.get_object()
        try:
            participation = Participation.objects.get(
                user=request.user, session=session
            )
            old_role = participation.role
            participation.delete()

            return Response({
                'status': 'left session',
                'was_role': old_role
            }, status=status.HTTP_200_OK)
        except Participation.DoesNotExist:
            return Response({
                'status': 'not in session'
            }, status=status.HTTP_400_BAD_REQUEST)

    def _broadcast_session_update(self, session, event_type, extra_data=None):
        """
        Broadcast session updates via WebSocket to all connected clients.

        Sends real-time updates about session status changes to all participants
        and viewers connected to the session's WebSocket group.

        Args:
            session: The DebateSession instance being updated.
            event_type: Type of event being broadcasted.
            extra_data: Optional additional data to include in broadcast.
        """
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        channel_layer = get_channel_layer()
        if not channel_layer:
            return

        # Prepare base message data
        data = {
            'type': 'session_status_update',
            'event_type': event_type,
            'session_status': session.status,
            'timestamp': timezone.now().isoformat()
        }

        # Add any extra data provided
        if extra_data:
            data.update(extra_data)

        # Add status-specific timing information
        if session.status == 'open':
            data['joining_window_end'] = (
                session.joining_window_end.isoformat()
                if session.joining_window_end else None
            )
        elif session.status == 'online':
            data['debate_end_time'] = (
                session.debate_end_time.isoformat()
                if session.debate_end_time else None
            )
        elif session.status == 'voting':
            data['voting_end_time'] = (
                session.voting_end_time.isoformat()
                if session.voting_end_time else None
            )
        elif session.status == 'finished':
            data.update({
                'winner': (
                    session.winner_participant.username
                    if session.winner_participant else None
                ),
                'total_votes': session.total_votes
            })

        # Broadcast to session group
        async_to_sync(channel_layer.group_send)(
            f'debate_{session.id}',
            data
        )

    @action(detail=True, methods=['get'], permission_classes=[])
    def status(self, request, pk=None):
        """
        Get enhanced session status with phase-aware information.

        Provides comprehensive session status including:
        - Current phase determination
        - Countdown timers to next phase
        - Real-time participant statistics
        - Session capability flags (can join, chat, vote)

        Args:
            request: The HTTP request object.
            pk: Primary key of the debate session.

        Returns:
            Response: Comprehensive session status information.
        """
        session = self.get_object()
        now = timezone.now()

        # Determine current phase based on timestamps
        if session.status == 'cancelled':
            phase = 'ended'
        elif not session.joining_started_at or now < session.joining_started_at:
            phase = 'offline'
        elif now < session.joining_window_end:
            phase = 'open'
        elif now < session.debate_started_at:
            phase = 'closed'
        elif now < session.debate_end_time:
            phase = 'online'
        elif session.voting_end_time and now < session.voting_end_time:
            phase = 'voting'
        else:
            phase = 'ended'

        # Calculate countdown to next phase
        countdown = None
        next_phase_label = None

        if phase == 'offline' and session.joining_started_at:
            countdown = int((session.joining_started_at - now).total_seconds())
            next_phase_label = "Joining opens"
        elif phase == 'open':
            countdown = int((session.joining_window_end - now).total_seconds())
            next_phase_label = "Joining closes"
        elif phase == 'closed':
            countdown = int((session.debate_started_at - now).total_seconds())
            next_phase_label = "Debate starts"
        elif phase == 'online':
            countdown = int((session.debate_end_time - now).total_seconds())
            next_phase_label = "Voting begins"
        elif phase == 'voting' and session.voting_end_time:
            countdown = int((session.voting_end_time - now).total_seconds())
            next_phase_label = "Session ends"

        # Gather real-time statistics
        participant_count = session.participation_set.filter(
            role='participant'
        ).count()
        viewer_count = session.participation_set.filter(role='viewer').count()
        message_count = session.messages.count()

        return Response({
            'phase': phase,
            'canJoin': phase == 'open',
            'canChat': phase == 'online',
            'canVote': phase == 'voting',
            'countdownToNextPhase': countdown,
            'nextPhaseLabel': next_phase_label,
            'participantCount': participant_count,
            'viewerCount': viewer_count,
            'messageCount': message_count,
            'sessionInfo': {
                'id': session.id,
                'title': session.topic.title,
                'description': session.topic.description,
                'moderator': (
                    session.moderator.username if session.moderator else None
                ),
                'duration_minutes': session.duration_minutes,
                'created_at': session.created_at.isoformat(),
            }
        })

    # @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    # def vote(self, request, pk=None):
    #     """
    #     Submit a vote for the session (viewers only).
    #     
    #     NOTE: This old voting method has been replaced by the new Vote model
    #     and voting API endpoints in vote_views.py
    #     """
    #     pass
    #     # OLD CODE COMMENTED OUT - REPLACED BY NEW VOTING SYSTEM
    #     # session = self.get_object()
    #     # vote_choice = request.data.get('vote')
    #     # best_argument_id = request.data.get('best_argument_message_id')
    #     #... (rest of old voting logic removed)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def user_vote_status(self, request, pk=None):
        """
        Check if user has voted in this session.

        Args:
            request: The HTTP request object.
            pk: Primary key of the debate session.

        Returns:
            Response: User's voting status and choice if applicable.
        """
        session = self.get_object()
        user_vote = DebateVote.objects.filter(
            session=session, voter=request.user
        ).first()

        return Response({
            'has_voted': user_vote is not None,
            'vote': user_vote.vote if user_vote else None
        })

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def voting_results(self, request, pk=None):
        """
        Get comprehensive voting results for a session.

        Provides detailed voting statistics including:
        - Vote counts by side
        - Winner determination
        - User's voting status
        - Participant information by side

        Args:
            request: The HTTP request object.
            pk: Primary key of the debate session.

        Returns:
            Response: Complete voting results and statistics.
        """
        session = self.get_object()

        # Get vote counts by side
        votes = DebateVote.objects.filter(session=session)
        proposition_votes = votes.filter(vote='proposition').count()
        opposition_votes = votes.filter(vote='opposition').count()
        total_votes = proposition_votes + opposition_votes

        # Check current user's voting status
        user_vote = None
        user_vote_obj = None
        if request.user.is_authenticated:
            user_vote_obj = votes.filter(voter=request.user).first()
            user_vote = user_vote_obj.vote if user_vote_obj else None

        # Determine winner
        if proposition_votes > opposition_votes:
            winner = 'proposition'
        elif opposition_votes > proposition_votes:
            winner = 'opposition'
        else:
            winner = 'tie'

        # Get participant information by side
        proposition_participants = session.participation_set.filter(
            role='participant', side='proposition'
        ).select_related('user').values('user__username', 'user__id')

        opposition_participants = session.participation_set.filter(
            role='participant', side='opposition'
        ).select_related('user').values('user__username', 'user__id')

        return Response({
            'proposition': proposition_votes,
            'opposition': opposition_votes,
            'total': total_votes,
            'hasVoted': user_vote is not None,
            'userVote': user_vote,
            'winner': winner,
            'participants': {
                'proposition': list(proposition_participants),
                'opposition': list(opposition_participants)
            },
            'voting_end_time': (
                session.voting_end_time.isoformat()
                if session.voting_end_time else None
            )
        })

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def transcript(self, request, pk=None):
        """
        Get session transcript with all messages.

        Retrieves a complete transcript of the debate session including
        all messages with timestamps and user information.

        Args:
            request: The HTTP request object.
            pk: Primary key of the debate session.

        Returns:
            Response: Complete session transcript with metadata.
        """
        session = self.get_object()

        # Get messages for transcript (ordered by timestamp)
        messages = Message.objects.filter(session=session).select_related(
            'user'
        ).order_by('timestamp')

        transcript_data = []
        for message in messages:
            transcript_data.append({
                'id': message.id,
                'timestamp': message.timestamp.isoformat(),
                'user': {
                    'id': message.user.id,
                    'username': message.user.username
                },
                'content': message.content,
                'message_type': getattr(message, 'message_type', 'text')
            })

        return Response({
            'session_id': session.id,
            'topic': session.topic.title,
            'transcript': transcript_data,
            'generated_at': timezone.now().isoformat()
        })

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def analytics(self, request, pk=None):
        """
        Get comprehensive session analytics and statistics.

        Provides detailed analytics including:
        - Message statistics and patterns
        - Participation metrics
        - Voting analytics and rates
        - Overall session performance data

        Args:
            request: The HTTP request object.
            pk: Primary key of the debate session.

        Returns:
            Response: Comprehensive session analytics data.
        """
        session = self.get_object()

        # Message analytics
        messages = session.messages.all()
        message_stats = {
            'total': messages.count(),
            'by_hour': {},  # TODO: Implement hourly message distribution
            'top_participants': []  # TODO: Implement top participants by message count
        }

        # Participation analytics
        participations = session.participation_set.all()
        participant_stats = {
            'total_participants': participations.filter(role='participant').count(),
            'total_viewers': participations.filter(role='viewer').count(),
            'muted_count': participations.filter(is_muted=True).count(),
            'warned_count': participations.filter(warnings_count__gt=0).count()
        }

        # Voting analytics
        votes = session.votes.all()
        total_voters = participant_stats['total_viewers']  # Only viewers can vote
        vote_stats = {
            'total_votes': votes.count(),
            'pro_votes': votes.filter(vote='proposition').count(),
            'con_votes': votes.filter(vote='opposition').count(),
            'participation_rate': 0
        }

        # Calculate voting participation rate
        if total_voters > 0:
            vote_stats['participation_rate'] = (
                (vote_stats['total_votes'] / total_voters) * 100
            )

        return Response({
            'session_id': session.id,
            'topic': session.topic.title,
            'duration_minutes': session.duration_minutes,
            'status': session.status,
            'messages': message_stats,
            'participants': participant_stats,
            'votes': vote_stats,
            'generated_at': timezone.now().isoformat()
        })

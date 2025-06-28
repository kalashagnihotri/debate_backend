"""
Session moderation actions for DebateSessionViewSet.
These actions are separated due to their complexity and specialized nature.
"""

from datetime import timedelta

from core.permissions import IsSessionModerator
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import ModerationAction, Participation
from notifications.models import Notification
from ..services.notification_service import notification_service

User = get_user_model()


class SessionModerationMixin:
    """Mixin containing moderation actions for DebateSessionViewSet"""

    @action(detail=True, methods=["post"], permission_classes=[IsSessionModerator])
    def mute_participant(self, request, pk=None):
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        session = self.get_object()
        user_id = request.data.get("user_id")
        reason = request.data.get("reason", "")
        user = get_object_or_404(User, id=user_id)
        participation, created = Participation.objects.get_or_create(
            user=user, session=session
        )
        participation.is_muted = True
        participation.save()

        # Log moderation action
        ModerationAction.objects.create(
            session=session,
            moderator=request.user,
            target_user=user,
            action="mute",
            reason=reason,
        )

        # Send moderation notification using service
        notification_service.send_moderation_action(
            session=session,
            target_user=user,
            moderator=request.user,
            action="mute",
            reason=reason,
        )

        # Broadcast moderation action via WebSocket
        channel_layer = get_channel_layer()
        if channel_layer:
            # Get updated participants list
            participants = []
            for participation in session.participation_set.select_related("user").all():
                participants.append(
                    {
                        "id": participation.user.id,
                        "username": participation.user.username,
                        "is_muted": participation.is_muted,
                        "is_online": True,  # You might want to track this properly
                    }
                )

            async_to_sync(channel_layer.group_send)(
                f"debate_{session.id}",
                {
                    "type": "moderation_action",
                    "action": "mute",
                    "target_user_id": user.id,
                    "target_username": user.username,
                    "moderator": request.user.username,
                    "reason": reason,
                    "participants": participants,
                },
            )

        return Response(
            {"status": f"user {user.username} muted"}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], permission_classes=[IsSessionModerator])
    def unmute_participant(self, request, pk=None):
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        session = self.get_object()
        user_id = request.data.get("user_id")
        user = get_object_or_404(User, id=user_id)
        participation, created = Participation.objects.get_or_create(
            user=user, session=session
        )
        participation.is_muted = False
        participation.save()

        # Log moderation action
        ModerationAction.objects.create(
            session=session, moderator=request.user, target_user=user, action="unmute"
        )

        # Send moderation notification using service
        notification_service.send_moderation_action(
            session=session, target_user=user, moderator=request.user, action="unmute"
        )

        # Broadcast moderation action via WebSocket
        channel_layer = get_channel_layer()
        if channel_layer:
            # Get updated participants list
            participants = []
            for participation in session.participation_set.select_related("user").all():
                participants.append(
                    {
                        "id": participation.user.id,
                        "username": participation.user.username,
                        "is_muted": participation.is_muted,
                        "is_online": True,  # You might want to track this properly
                    }
                )

            async_to_sync(channel_layer.group_send)(
                f"debate_{session.id}",
                {
                    "type": "moderation_action",
                    "action": "unmute",
                    "target_user_id": user.id,
                    "target_username": user.username,
                    "moderator": request.user.username,
                    "participants": participants,
                },
            )

        return Response(
            {"status": f"user {user.username} unmuted"}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], permission_classes=[IsSessionModerator])
    def warn_participant(self, request, pk=None):
        """Warn a participant"""
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        session = self.get_object()
        user_id = request.data.get("user_id")
        reason = request.data.get("reason", "")
        user = get_object_or_404(User, id=user_id)
        participation, created = Participation.objects.get_or_create(
            user=user, session=session
        )
        participation.warnings_count += 1
        participation.save()

        # Log moderation action
        ModerationAction.objects.create(
            session=session,
            moderator=request.user,
            target_user=user,
            action="warn",
            reason=reason,
        )

        # Create notification
        Notification.objects.create(
            recipient=user,
            sender=request.user,
            notification_type="moderation_action",
            title="Warning issued",
            message=f'You have received a warning in the debate "{session.topic.title}". Reason: {reason}',
            session=session,
        )

        # Broadcast moderation action via WebSocket
        channel_layer = get_channel_layer()
        if channel_layer:
            # Get updated participants list
            participants = []
            for participation in session.participation_set.select_related("user").all():
                participants.append(
                    {
                        "id": participation.user.id,
                        "username": participation.user.username,
                        "is_muted": participation.is_muted,
                        "warnings_count": participation.warnings_count,
                        "is_online": True,
                    }
                )

            async_to_sync(channel_layer.group_send)(
                f"debate_{session.id}",
                {
                    "type": "moderation_action",
                    "action": "warn",
                    "target_user_id": user.id,
                    "target_username": user.username,
                    "moderator": request.user.username,
                    "reason": reason,
                    "warnings_count": participation.warnings_count,
                    "participants": participants,
                },
            )

        return Response(
            {
                "status": f"user {user.username} warned",
                "warnings": participation.warnings_count,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], permission_classes=[IsSessionModerator])
    def remove_participant(self, request, pk=None):
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        session = self.get_object()
        user_id = request.data.get("user_id")
        reason = request.data.get("reason", "")
        user = get_object_or_404(User, id=user_id)

        # Log moderation action before removing
        ModerationAction.objects.create(
            session=session,
            moderator=request.user,
            target_user=user,
            action="remove",
            reason=reason,
        )

        # Create notification
        Notification.objects.create(
            recipient=user,
            sender=request.user,
            notification_type="moderation_action",
            title="Removed from debate",
            message=f'You have been removed from the debate "{session.topic.title}". Reason: {reason}',
            session=session,
        )

        # Remove participation
        Participation.objects.filter(user=user, session=session).delete()

        # Broadcast moderation action via WebSocket
        channel_layer = get_channel_layer()
        if channel_layer:
            # Get updated participants list (after removal)
            participants = []
            for participation in session.participation_set.select_related("user").all():
                participants.append(
                    {
                        "id": participation.user.id,
                        "username": participation.user.username,
                        "is_muted": participation.is_muted,
                        "warnings_count": participation.warnings_count,
                        "is_online": True,
                    }
                )

            async_to_sync(channel_layer.group_send)(
                f"debate_{session.id}",
                {
                    "type": "moderation_action",
                    "action": "remove",
                    "target_user_id": user.id,
                    "target_username": user.username,
                    "moderator": request.user.username,
                    "reason": reason,
                    "participants": participants,
                },
            )

        return Response(
            {"status": f"user {user.username} removed"}, status=status.HTTP_200_OK
        )

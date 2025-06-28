"""
Modern notification service for the debate platform.

Handles all notification delivery through WebSocket and stores notifications
for the bell icon interface. Provides comprehensive notification management
including delivery, tracking, and cleanup operations.
"""

import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service class for handling all notification operations.

    Provides comprehensive notification management including:
    - Multi-recipient notification sending
    - WebSocket delivery
    - Database persistence
    - Expiration handling
    - Session-specific notifications
    """

    def __init__(self):
        self.channel_layer = get_channel_layer()

    def send_notification(
        self,
        recipients,
        notification_type,
        title,
        message,
        sender=None,
        session=None,
        priority='normal',
        action_url=None,
        action_label=None,
        expires_in_minutes=None,
        delivery_method='websocket'
    ):
        """
        Send notifications to multiple recipients.

        Args:
            recipients: List of User objects to receive notifications.
            notification_type: Type of notification (string identifier).
            title: Notification title.
            message: Notification message content.
            sender: User object of notification sender (optional).
            session: Related DebateSession object (optional).
            priority: Notification priority ('low', 'normal', 'high').
            action_url: URL for notification action (optional).
            action_label: Label for notification action button (optional).
            expires_in_minutes: Notification expiration time in minutes (optional).
            delivery_method: Delivery method ('websocket', 'email', 'both').

        Returns:
            List of created Notification objects.
        """
        # Import here to avoid circular imports
        from notifications.models import Notification

        notifications = []
        expires_at = None

        if expires_in_minutes:
            expires_at = timezone.now() + timedelta(minutes=expires_in_minutes)

        for recipient in recipients:
            # Create notification record
            notification = Notification.objects.create(
                recipient=recipient,
                sender=sender,
                notification_type=notification_type,
                priority=priority,
                title=title,
                message=message,
                session=session,
                action_url=action_url,
                action_label=action_label,
                expires_at=expires_at,
                delivery_method=delivery_method
            )
            notifications.append(notification)

            # Send via WebSocket if requested
            if delivery_method in ['websocket', 'both']:
                self._send_websocket_notification(notification)

        return notifications

    def _send_websocket_notification(self, notification):
        """
        Send notification via WebSocket to user's personal channel.

        Args:
            notification: Notification object to send via WebSocket.
        """
        if not self.channel_layer:
            logger.warning("Channel layer not available for WebSocket notification")
            return

        # Send to user's personal notification channel
        user_channel = f"notifications_{notification.recipient.id}"

        notification_data = {
            'type': 'notification_received',
            'notification': {
                'id': notification.id,
                'type': notification.notification_type,
                'priority': notification.priority,
                'title': notification.title,
                'message': notification.message,
                'timestamp': notification.timestamp.isoformat(),
                'action_url': notification.action_url,
                'action_label': notification.action_label,
                'session_id': notification.session.id if notification.session else None,
                'sender': notification.sender.username if notification.sender else None,
            }
        }

        try:
            async_to_sync(self.channel_layer.group_send)(
                user_channel,
                notification_data
            )
            notification.mark_as_delivered()
            logger.info(f"Notification sent to {notification.recipient.username}")
        except Exception as e:
            logger.error(f"Failed to send WebSocket notification: {e}")

    def send_session_notification(
        self,
        session,
        notification_type,
        title,
        message,
        sender=None,
        priority='normal',
        action_url=None,
        action_label=None,
        expires_in_minutes=None,
        include_participants=True,
        include_viewers=True,
        include_moderator=True
    ):
        """
        Send notifications to all session participants/viewers
        """
        recipients = []

        # Get session participants and viewers
        participations = session.participation_set.select_related('user').all()

        for participation in participations:
            if participation.role == 'participant' and include_participants:
                recipients.append(participation.user)
            elif participation.role == 'viewer' and include_viewers:
                recipients.append(participation.user)

        # Include moderator if requested
        if include_moderator and session.moderator:
            recipients.append(session.moderator)

        # Remove duplicates
        recipients = list(set(recipients))

        return self.send_notification(
            recipients=recipients,
            notification_type=notification_type,
            title=title,
            message=message,
            sender=sender,
            session=session,
            priority=priority,
            action_url=action_url,
            action_label=action_label,
            expires_in_minutes=expires_in_minutes
        )

    def notify_all_users_debate_starting(self, session):
        """
        Notify all online users (excluding session participants) about a debate starting
        """
        try:
            # Get all active users who are not already in the session
            all_users = User.objects.filter(is_active=True)
            session_participant_ids = session.participation_set.values_list(
                'user_id', flat=True)

            # Filter out users already participating in this session
            recipients = [
                user for user in all_users if user.id not in session_participant_ids]

            # Limit to first 100 users to avoid overwhelming the system
            recipients = recipients[:100]

            if recipients:
                return self.send_notification(
                    recipients=recipients,
                    notification_type='session_starting',
                    title=f'🔥 New Debate Starting: {session.topic.title}',
                    message=f'A new debate on "{session.topic.title}" is starting! Join now during the 5-minute joining window.',
                    sender=session.moderator,
                    session=session,
                    priority='high',
                    action_url=f'/debates/{session.id}',
                    action_label='Join Debate',
                    expires_in_minutes=10,
                    delivery_method='websocket'
                )
        except Exception as e:
            logger.error(f"Failed to notify all users about debate starting: {e}")
            return []

    def send_joining_window_opened(self, session):
        """
        Notify about joining window opening.

        Args:
            session: DebateSession object for which joining window opened.
        """
        return self.send_session_notification(
            session=session,
            notification_type='joining_opened',
            title=f'Debate starting: {session.topic.title}',
            message='The joining window is now open! You have 5 minutes to join as a participant.',
            priority='high',
            action_url=f'/debates/{session.id}',
            action_label='Join Now',
            expires_in_minutes=5,
            include_participants=False,
            include_viewers=False,
            include_moderator=False
        )

    def send_joining_window_closing(self, session):
        """
        Notify about joining window closing soon.

        Args:
            session: DebateSession object for which joining window is closing.
        """
        return self.send_session_notification(
            session=session,
            notification_type='joining_closing',
            title=f'Last chance to join: {session.topic.title}',
            message='Joining window closes in 1 minute! Join now as a participant.',
            priority='urgent',
            action_url=f'/debates/{session.id}',
            action_label='Join Now',
            expires_in_minutes=1
        )

    def send_debate_started(self, session):
        """
        Notify about debate chat being unlocked.

        Args:
            session: DebateSession object for which debate started.
        """
        return self.send_session_notification(
            session=session,
            notification_type='debate_started',
            title='💬 Debate Chat Unlocked!',
            message=f'The debate on "{session.topic.title}" has started. Participants can now chat!',
            sender=session.moderator,
            priority='normal',
            action_url=f'/debates/{session.id}',
            action_label='Join Chat',
            expires_in_minutes=session.duration_minutes
        )

    def send_voting_started(self, session):
        """
        Notify about voting period starting.

        Args:
            session: DebateSession object for which voting started.
        """
        return self.send_session_notification(
            session=session,
            notification_type='voting_started',
            title='🗳️ Voting Started!',
            message=f'The debate on "{session.topic.title}" has ended. Vote for the best participant now! (30 seconds)',
            sender=session.moderator,
            priority='high',
            action_url=f'/debates/{session.id}',
            action_label='Vote Now',
            expires_in_minutes=1,
            include_participants=False,  # Only viewers can vote
            include_viewers=True,
            include_moderator=False
        )

    def send_session_finished(self, session):
        """
        Notify about session completion.

        Args:
            session: DebateSession object that has finished.
        """
        winner_text = ""
        if session.winner_participant:
            winner_text = f" Winner: {session.winner_participant.username}"

        return self.send_session_notification(
            session=session,
            notification_type='session_finished',
            title=f'Debate finished: {session.topic.title}',
            message=f'The debate has concluded with {session.total_votes} votes.{winner_text}',
            priority='normal',
            action_url=f'/debates/{session.id}',
            action_label='View Results'
        )

    def send_moderation_action(
        self,
        session,
        target_user,
        moderator,
        action,
        reason=""
    ):
        """Send notification for moderation actions"""
        action_messages = {
            'mute': f'You have been muted in "{session.topic.title}"',
            'unmute': f'You have been unmuted in "{session.topic.title}"',
            'warn': f'You received a warning in "{session.topic.title}"',
            'kick': f'You have been removed from "{session.topic.title}"',
        }

        message = action_messages.get(action, f'Moderation action: {action}')
        if reason:
            message += f' Reason: {reason}'

        return self.send_notification(
            recipients=[target_user],
            notification_type='moderation_action',
            title='Moderation Action',
            message=message,
            sender=moderator,
            session=session,
            priority='high' if action in ['kick', 'mute'] else 'normal'
        )

    def get_user_notifications(
        self,
        user,
        unread_only=False,
        limit=50
    ):
        """Get notifications for a user"""
        queryset = user.debate_notifications.select_related('sender', 'session__topic')

        if unread_only:
            queryset = queryset.filter(is_read=False)

        # Filter out expired notifications
        queryset = queryset.filter(
            models.Q(expires_at__isnull=True) |
            models.Q(expires_at__gt=timezone.now())
        )

        return list(queryset[:limit])

    def mark_notifications_as_read(self, user, notification_ids=None):
        """Mark notifications as read"""
        queryset = user.debate_notifications.filter(is_read=False)

        if notification_ids:
            queryset = queryset.filter(id__in=notification_ids)

        updated_count = queryset.update(
            is_read=True,
            read_at=timezone.now()
        )

        return updated_count

    def get_unread_count(self, user):
        """Get count of unread notifications for user"""
        return user.debate_notifications.filter(
            is_read=False,
            is_dismissed=False
        ).filter(
            models.Q(expires_at__isnull=True) |
            models.Q(expires_at__gt=timezone.now())
        ).count()


# Global service instance
notification_service = NotificationService()

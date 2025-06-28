"""
Notification service for creating and managing notifications.

Provides functionality for:
- Creating notifications
- Sending real-time notifications via WebSocket
- Scheduling notifications for upcoming debates
"""

import logging
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Notification

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationService:
    """Service class for managing notifications"""

    def create_notification(self, user, message, notification_type):
        """
        Create a new notification for a user.

        Args:
            user: User instance to notify
            message: Notification message text
            notification_type: Type of notification (UPCOMING_DEBATE, SESSION_CHANGE, MODERATION_ACTION)

        Returns:
            Notification: Created notification instance
        """
        try:
            notification = Notification.objects.create(
                user=user, message=message, type=notification_type
            )

            # Send real-time notification via WebSocket
            self._send_realtime_notification(user, notification)

            logger.info(
                f"Notification created for user {user.username}: {notification_type}"
            )
            return notification

        except Exception as e:
            logger.error(f"Error creating notification: {str(e)}")
            return None

    def create_bulk_notifications(self, users, message, notification_type):
        """
        Create notifications for multiple users.

        Args:
            users: QuerySet or list of User instances
            message: Notification message text
            notification_type: Type of notification

        Returns:
            List of created notification instances
        """
        notifications = []
        for user in users:
            notification = self.create_notification(user, message, notification_type)
            if notification:
                notifications.append(notification)

        return notifications

    def notify_upcoming_debate(self, debate_session, minutes_before=60):
        """
        Send notifications for upcoming debates.

        Args:
            debate_session: DebateSession instance
            minutes_before: Minutes before start to send notification
        """
        try:
            # Get all users who should be notified (students and moderators)
            users_to_notify = User.objects.filter(role__in=["student", "moderator"])

            message = f"Debate '{debate_session.topic.title}' starts in {minutes_before} minutes"

            self.create_bulk_notifications(users_to_notify, message, "UPCOMING_DEBATE")

            logger.info(
                f"Upcoming debate notifications sent for session {debate_session.id}"
            )

        except Exception as e:
            logger.error(f"Error sending upcoming debate notifications: {str(e)}")

    def notify_session_change(self, debate_session, change_message):
        """
        Send notifications for session changes.

        Args:
            debate_session: DebateSession instance
            change_message: Description of the change
        """
        try:
            # Notify all participants in the session
            participants = debate_session.participants.all()

            message = f"Session '{debate_session.topic.title}' update: {change_message}"

            self.create_bulk_notifications(participants, message, "SESSION_CHANGE")

            logger.info(
                f"Session change notifications sent for session {debate_session.id}"
            )

        except Exception as e:
            logger.error(f"Error sending session change notifications: {str(e)}")

    def notify_moderation_action(self, target_user, moderator, action, reason):
        """
        Send notification for moderation actions.

        Args:
            target_user: User who was moderated
            moderator: User who performed the action
            action: Type of moderation action
            reason: Reason for the action
        """
        try:
            message = (
                f"Moderation action by {moderator.username}: {action}. Reason: {reason}"
            )

            self.create_notification(target_user, message, "MODERATION_ACTION")

            logger.info(
                f"Moderation action notification sent to {target_user.username}"
            )

        except Exception as e:
            logger.error(f"Error sending moderation action notification: {str(e)}")

    def _send_realtime_notification(self, user, notification):
        """
        Send real-time notification via WebSocket.

        Args:
            user: User to notify
            notification: Notification instance
        """
        try:
            from debates.services.websocket_service import broadcast_notification

            notification_data = {
                "id": notification.id,
                "message": notification.message,
                "type": notification.type,
                "type_display": notification.get_type_display(),
                "is_read": notification.is_read,
                "created_at": notification.created_at.isoformat(),
            }

            broadcast_notification([user.id], notification_data)

        except ImportError:
            logger.warning(
                "WebSocket service not available for real-time notifications"
            )
        except Exception as e:
            logger.error(f"Error sending real-time notification: {str(e)}")

    def mark_notifications_as_read(self, user, notification_ids=None):
        """
        Mark notifications as read for a user.

        Args:
            user: User instance
            notification_ids: List of notification IDs to mark as read (optional)

        Returns:
            int: Number of notifications marked as read
        """
        try:
            notifications = Notification.objects.filter(user=user, is_read=False)

            if notification_ids:
                notifications = notifications.filter(id__in=notification_ids)

            updated_count = notifications.update(is_read=True)
            logger.info(
                f"Marked {updated_count} notifications as read for user {user.username}"
            )

            return updated_count

        except Exception as e:
            logger.error(f"Error marking notifications as read: {str(e)}")
            return 0


# Create singleton instance
notification_service = NotificationService()


# Celery tasks for scheduled notifications
try:
    from celery import shared_task

    @shared_task
    def send_upcoming_debate_notifications():
        """
        Celery task to send notifications for upcoming debates.
        Should be run every 5 minutes to check for debates starting soon.
        """
        from debates.models import DebateSession

        # Find debates starting in the next hour
        now = timezone.now()
        upcoming_time = now + timedelta(hours=1)

        upcoming_sessions = DebateSession.objects.filter(
            scheduled_start__gte=now,
            scheduled_start__lte=upcoming_time,
            status="offline",
        )

        for session in upcoming_sessions:
            minutes_until_start = int(
                (session.scheduled_start - now).total_seconds() / 60
            )
            notification_service.notify_upcoming_debate(session, minutes_until_start)

        return f"Processed {upcoming_sessions.count()} upcoming debate notifications"

except ImportError:
    logger.warning("Celery not available - scheduled notifications will not work")

    def send_upcoming_debate_notifications():
        """Fallback function when Celery is not available"""
        logger.warning("Celery not configured - cannot send scheduled notifications")
        return "Celery not available"

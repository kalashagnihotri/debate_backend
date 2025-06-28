"""
Notification API views.

Provides notification functionality as per requirements:
- GET /api/v1/notifications/: Retrieve notifications for the logged-in user
- POST /api/v1/notifications/mark_as_read/: Mark notifications as read
"""

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    """
    Retrieve notifications for the logged-in user.

    GET /api/v1/notifications/

    Query parameters:
    - is_read: Filter by read status (true/false)
    - type: Filter by notification type
    - limit: Limit number of results (default: 50)

    Response:
    {
        "notifications": [
            {
                "id": 1,
                "message": "Debate starts in 1 hour",
                "type": "UPCOMING_DEBATE",
                "is_read": false,
                "created_at": "2025-06-27T10:00:00Z"
            }
        ],
        "total_count": 1,
        "unread_count": 1
    }
    """
    try:
        # Get query parameters
        is_read_param = request.query_params.get("is_read")
        notification_type = request.query_params.get("type")
        limit = int(request.query_params.get("limit", 50))

        # Build queryset
        notifications = Notification.objects.filter(user=request.user)

        # Apply filters
        if is_read_param is not None:
            is_read = is_read_param.lower() == "true"
            notifications = notifications.filter(is_read=is_read)

        if notification_type:
            notifications = notifications.filter(type=notification_type)

        # Get counts
        total_count = notifications.count()
        unread_count = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()

        # Apply limit and serialize
        notifications = notifications[:limit]
        serializer = NotificationSerializer(notifications, many=True)

        return Response(
            {
                "notifications": serializer.data,
                "total_count": total_count,
                "unread_count": unread_count,
            }
        )

    except Exception as e:
        logger.error(f"Error retrieving notifications: {str(e)}")
        return Response(
            {"error": "An error occurred while retrieving notifications"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_notifications_as_read(request):
    """
    Mark notifications as read.

    POST /api/v1/notifications/mark_as_read/

    Request body:
    {
        "notification_ids": [1, 2, 3]
    }

    If notification_ids is empty or not provided, all unread notifications
    for the user will be marked as read.
    """
    try:
        notification_ids = request.data.get("notification_ids", [])

        # Build queryset for user's notifications
        notifications = Notification.objects.filter(user=request.user, is_read=False)

        # Filter by specific IDs if provided
        if notification_ids:
            notifications = notifications.filter(id__in=notification_ids)

        # Mark as read
        updated_count = notifications.update(is_read=True)

        return Response(
            {
                "message": f"{updated_count} notifications marked as read",
                "updated_count": updated_count,
            }
        )

    except Exception as e:
        logger.error(f"Error marking notifications as read: {str(e)}")
        return Response(
            {"error": "An error occurred while marking notifications as read"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_notification_stats(request):
    """
    Get notification statistics for the logged-in user.

    GET /api/v1/notifications/stats/

    Response:
    {
        "total_notifications": 10,
        "unread_count": 3,
        "by_type": {
            "UPCOMING_DEBATE": 2,
            "SESSION_CHANGE": 1,
            "MODERATION_ACTION": 0
        }
    }
    """
    try:
        user_notifications = Notification.objects.filter(user=request.user)

        total_notifications = user_notifications.count()
        unread_count = user_notifications.filter(is_read=False).count()

        # Count by type
        by_type = {}
        for choice_value, choice_label in Notification.TYPE_CHOICES:
            by_type[choice_value] = user_notifications.filter(type=choice_value).count()

        return Response(
            {
                "total_notifications": total_notifications,
                "unread_count": unread_count,
                "by_type": by_type,
            }
        )

    except Exception as e:
        logger.error(f"Error retrieving notification stats: {str(e)}")
        return Response(
            {"error": "An error occurred while retrieving notification statistics"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

"""
URL configuration for notifications app.

Provides URL patterns for notification-related API endpoints.
"""

from django.urls import path
from .views import get_notifications, mark_notifications_as_read, get_notification_stats

urlpatterns = [
    # Notification API endpoints as per requirements
    path("", get_notifications, name="get-notifications"),
    path("mark_as_read/", mark_notifications_as_read, name="mark-notifications-read"),
    path("stats/", get_notification_stats, name="notification-stats"),
]

"""
Django admin configuration for notifications app.

Provides admin interface for notification management.
"""

from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for notifications."""

    list_display = ("user", "type", "message", "is_read", "created_at")
    list_filter = ("type", "is_read", "created_at")
    search_fields = ("user__username", "message")
    readonly_fields = ("created_at",)

    def mark_as_read(self, request, queryset):
        """Action to mark selected notifications as read"""
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} notifications marked as read.")

    mark_as_read.short_description = "Mark selected notifications as read"
    actions = [mark_as_read]

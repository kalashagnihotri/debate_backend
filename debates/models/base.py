"""
Base model utilities and shared imports for the debates models.
"""

from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


# Common model mixins
class TimestampedMixin(models.Model):
    """Mixin to add created_at and updated_at fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class StatusMixin(models.Model):
    """Mixin for models that have status fields"""
    class Meta:
        abstract = True

    def get_status_display_with_icon(self):
        """Get status display with appropriate icon"""
        status_icons = {
            'offline': '⚫',
            'open': '🟢',
            'closed': '🟡',
            'online': '🔴',
            'voting': '🗳️',
            'finished': '✅',
            'cancelled': '❌',
        }
        return f"{status_icons.get(self.status, '')} {self.get_status_display()}"

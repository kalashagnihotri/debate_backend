"""
Participation model for tracking user involvement in debates.

This module defines the Participation model which tracks how users
participate in debate sessions, including their role, side, activity metrics,
and moderation status.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import TimestampedMixin


class Participation(TimestampedMixin):
    """
    Model tracking user participation in debate sessions.

    Manages user roles, sides, activity metrics, and moderation status
    within specific debate sessions.
    """

    ROLE_CHOICES = [
        ("participant", "Participant"),
        ("viewer", "Viewer"),
    ]

    SIDE_CHOICES = [
        ("proposition", "Proposition"),
        ("opposition", "Opposition"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session = models.ForeignKey("DebateSession", on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="viewer")
    side = models.CharField(max_length=20, choices=SIDE_CHOICES, null=True, blank=True)

    joined_at = models.DateTimeField(default=timezone.now)
    is_muted = models.BooleanField(default=False)
    warnings_count = models.IntegerField(default=0)
    messages_sent = models.IntegerField(default=0)

    # Participation tracking
    is_participant = models.BooleanField(
        default=False, help_text="True if actively participating"
    )
    last_activity = models.DateTimeField(auto_now=True)

    # Performance metrics
    words_spoken = models.IntegerField(default=0)
    arguments_made = models.IntegerField(default=0)
    questions_asked = models.IntegerField(default=0)

    class Meta:
        unique_together = ("user", "session")
        verbose_name = "Participation"
        verbose_name_plural = "Participations"

    def __str__(self):
        return f"{self.user.username} - {self.role} in {self.session}"

    def clean(self):
        """
        Validate participation data.

        Ensures participants have a side and viewers don't have sides.

        Raises:
            ValidationError: If participant lacks a side.
        """
        # Participants must have a side
        if self.role == "participant" and not self.side:
            raise ValidationError(
                "Participants must choose a side (proposition or opposition)"
            )

        # Viewers cannot have a side
        if self.role == "viewer" and self.side:
            self.side = None

"""
Message model for debate communications.

This module defines the Message model which handles all communication
within debate sessions, including text messages, system announcements,
reactions, and moderation features.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone

from .base import TimestampedMixin


class Message(TimestampedMixin):
    """
    Model representing messages in debate sessions.

    Handles various message types including text, images, system messages,
    and reactions. Includes support for threading, moderation, and engagement metrics.
    """
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('system', 'System'),
        ('announcement', 'Announcement'),
        ('reaction', 'Reaction'),
    ]

    session = models.ForeignKey(
        'DebateSession', related_name='messages', on_delete=models.CASCADE
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    message_type = models.CharField(
        max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text'
    )

    # Message metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # For system messages
    is_system_message = models.BooleanField(default=False)

    # Engagement metrics
    likes_count = models.IntegerField(default=0)
    reactions_count = models.IntegerField(default=0)

    # Media support
    image_url = models.URLField(blank=True, null=True)
    attachment_url = models.URLField(blank=True, null=True)

    # Reply threading
    reply_to = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE,
        related_name='replies'
    )

    # Moderation
    is_flagged = models.BooleanField(default=False)
    flagged_reason = models.CharField(max_length=255, blank=True)
    is_hidden = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"

    @property
    def is_reply(self):
        """Check if this message is a reply to another message."""
        return self.reply_to is not None

    @property
    def replies_count(self):
        """Count of replies to this message."""
        return self.replies.count()

    def soft_delete(self):
        """Soft delete the message."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def flag(self, reason=""):
        """Flag the message for moderation."""
        self.is_flagged = True
        self.flagged_reason = reason
        self.save()

    def hide(self):
        """Hide the message from public view."""
        self.is_hidden = True
        self.save()

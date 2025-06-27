"""
Moderation action models for tracking moderator actions.
"""

from django.conf import settings
from django.db import models

from .session_models import DebateSession


class ModerationAction(models.Model):
    ACTION_CHOICES = [
        ('mute', 'Mute'),
        ('unmute', 'Unmute'),
        ('remove', 'Remove'),
        ('warn', 'Warn'),
        ('kick', 'Kick'),
        ('force_phase_transition', 'Force Phase Transition'),
    ]

    session = models.ForeignKey(
        DebateSession,
        on_delete=models.CASCADE,
        related_name='moderation_actions')
    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='moderation_actions_taken')
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='moderation_actions_received',
        null=True,
        blank=True)
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    reason = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        if self.target_user:
            return f"{self.moderator.username} {self.action} {self.target_user.username}"
        return f"{self.moderator.username} {self.action}"

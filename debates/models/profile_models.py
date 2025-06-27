"""
User profile models for debate-specific user data.
"""

from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='debate_profile')
    total_debates_participated = models.IntegerField(default=0)
    total_debates_won = models.IntegerField(default=0)
    total_messages_sent = models.IntegerField(default=0)
    total_votes_cast = models.IntegerField(default=0)
    reputation_score = models.IntegerField(default=0)
    email_notifications = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        ordering = ['-reputation_score']

"""
Voting models for debate sessions.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone

from .message_models import Message
from .session_models import DebateSession


class DebateVote(models.Model):
    """Side-based voting model for viewers to vote for winning side"""

    VOTE_CHOICES = [
        ("proposition", "Proposition"),
        ("opposition", "Opposition"),
    ]

    session = models.ForeignKey(
        DebateSession, on_delete=models.CASCADE, related_name="votes"
    )
    voter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="debate_votes"
    )
    vote = models.CharField(
        max_length=20,
        choices=VOTE_CHOICES,
        help_text="Which side the voter believes won",
    )
    best_argument_message = models.ForeignKey(
        Message,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Optional: message that voter considers best argument",
    )
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("session", "voter")
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.voter.username} voted {self.vote} in {self.session}"

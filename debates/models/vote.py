"""
Voting model for debate outcomes.

This module defines the Vote model which handles voting functionality
for debate sessions, including vote types, best argument selection,
and vote metadata tracking as per requirements.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import TimestampedMixin


class Vote(models.Model):
    """
    Model representing votes cast in debate sessions.

    As per requirements:
    - Only students can vote
    - A user can vote only once per debate session
    - Supports BEST_ARGUMENT and WINNING_SIDE vote types
    """

    VOTE_TYPE_CHOICES = [
        ("BEST_ARGUMENT", "Best Argument"),
        ("WINNING_SIDE", "Winning Side"),
    ]

    # Required fields as per specifications
    id = models.BigAutoField(primary_key=True)
    debate_session = models.ForeignKey(
        "DebateSession",
        related_name="votes",
        on_delete=models.CASCADE,
        help_text="The debate session this vote belongs to",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="The user who cast this vote (must be a student)",
    )
    vote_type = models.CharField(
        max_length=20,
        choices=VOTE_TYPE_CHOICES,
        help_text="Type of vote: BEST_ARGUMENT or WINNING_SIDE",
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        # Ensure a user can only vote once per debate session
        unique_together = ("debate_session", "user")
        verbose_name = "Vote"
        verbose_name_plural = "Votes"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["debate_session", "vote_type"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} voted ({self.vote_type}) in {self.debate_session}"

    def clean(self):
        """Validate vote constraints"""
        super().clean()

        # Only students can vote
        if hasattr(self.user, "role") and self.user.role != "student":
            raise ValidationError("Only students can vote")

        # Check if user already voted
        if self.pk is None:  # Only for new votes
            existing_vote = Vote.objects.filter(
                debate_session=self.debate_session, user=self.user
            ).exists()
            if existing_vote:
                raise ValidationError("User has already voted in this session")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


# Keep the old DebateVote model for backward compatibility
class DebateVote(Vote):
    """
    Proxy model for backward compatibility.
    Maps to the new Vote model with WINNING_SIDE type.
    """

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        # Set vote_type to WINNING_SIDE for backward compatibility
        if not self.vote_type:
            self.vote_type = "WINNING_SIDE"
        super().save(*args, **kwargs)

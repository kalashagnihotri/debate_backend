"""
Moderation models for debate management.
"""

from django.conf import settings
from django.db import models

from .base import TimestampedMixin


class ModerationAction(TimestampedMixin):
    ACTION_CHOICES = [
        ("warn", "Warning"),
        ("mute", "Mute"),
        ("unmute", "Unmute"),
        ("remove", "Remove Participant"),
        ("ban", "Ban User"),
        ("timeout", "Timeout"),
        ("force_phase_transition", "Force Phase Transition"),
    ]

    session = models.ForeignKey(
        "DebateSession", on_delete=models.CASCADE, related_name="moderation_actions"
    )
    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="moderation_actions_taken",
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="moderation_actions_received",
        null=True,
        blank=True,
    )
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    reason = models.TextField(blank=True)

    # Action metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Additional context
    severity = models.CharField(
        max_length=10,
        choices=[
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        default="medium",
    )

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Moderation Action"
        verbose_name_plural = "Moderation Actions"

    def __str__(self):
        target = self.target_user.username if self.target_user else "Session"
        return f"{self.moderator.username} {self.action} {target}"


class UserProfile(TimestampedMixin):
    """Extended user profile for debate platform"""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Profile information
    bio = models.TextField(blank=True, max_length=500)
    avatar_url = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)

    # Debate statistics
    debates_participated = models.IntegerField(default=0)
    debates_won = models.IntegerField(default=0)
    total_votes_received = models.IntegerField(default=0)
    messages_sent = models.IntegerField(default=0)

    # Reputation and moderation
    reputation_score = models.IntegerField(default=0)
    warnings_received = models.IntegerField(default=0)
    is_banned = models.BooleanField(default=False)
    ban_expires_at = models.DateTimeField(null=True, blank=True)

    # Preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    show_online_status = models.BooleanField(default=True)

    # Activity tracking
    last_active = models.DateTimeField(auto_now=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def win_rate(self):
        """Calculate win rate percentage"""
        if self.debates_participated == 0:
            return 0
        return (self.debates_won / self.debates_participated) * 100

    @property
    def is_experienced(self):
        """Check if user is experienced (10+ debates)"""
        return self.debates_participated >= 10

    @property
    def reputation_level(self):
        """Get reputation level based on score"""
        if self.reputation_score < 100:
            return "Novice"
        elif self.reputation_score < 500:
            return "Intermediate"
        elif self.reputation_score < 1000:
            return "Advanced"
        else:
            return "Expert"


class SessionTranscript(TimestampedMixin):
    """Transcript of a debate session"""

    session = models.OneToOneField(
        "DebateSession", on_delete=models.CASCADE, related_name="transcript"
    )

    # Transcript content
    content = models.TextField(blank=True)
    formatted_content = models.TextField(blank=True)  # HTML formatted version

    # Generation metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="generated_transcripts",
    )

    # Processing status
    is_processed = models.BooleanField(default=False)
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)

    # Statistics
    total_messages = models.IntegerField(default=0)
    total_participants = models.IntegerField(default=0)
    word_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Session Transcript"
        verbose_name_plural = "Session Transcripts"

    def __str__(self):
        return f"Transcript for {self.session}"

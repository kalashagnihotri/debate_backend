"""
Session model for debates with lifecycle management.

This module defines the DebateSession model which manages the complete
lifecycle of a debate session from creation through completion, including
participant management, timing, and status transitions.
"""

from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import StatusMixin, TimestampedMixin
from .topic import DebateTopic


class DebateSession(TimestampedMixin, StatusMixin):
    """
    Model representing a debate session with complete lifecycle management.

    Handles session phases from offline through completion, including:
    - Participant joining windows
    - Debate timing and moderation
    - Voting periods and result calculation
    - Status transitions and validation
    """
    STATUS_CHOICES = [
        ('offline', 'Offline'),     # Not started - moderator hasn't opened joining
        ('open', 'Open'),           # 5-min joining window active
        ('closed', 'Closed'),       # Joining closed - only viewers can join
        ('online', 'Online'),       # Debate active - chat unlocked
        ('voting', 'Voting'),       # 30-second voting period
        ('finished', 'Finished'),   # Voting ended - results calculated
        ('cancelled', 'Cancelled'),  # Session cancelled by moderator
    ]

    topic = models.ForeignKey(
        DebateTopic,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='moderated_sessions',
        on_delete=models.SET_NULL,
        null=True
    )

    # Scheduling and Duration
    scheduled_start = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Optional scheduled start time for the session"
    )
    duration_minutes = models.IntegerField(
        default=60,
        help_text="Debate duration in minutes (20-180)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='offline'
    )

    # Session lifecycle timestamps
    joining_started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When joining window opened (5 min window)"
    )
    joining_window_end = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When joining window closes"
    )
    debate_started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When debate chat was unlocked"
    )
    debate_end_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When debate will/did end"
    )
    voting_started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When 30-second voting period started"
    )
    voting_end_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When voting period ended"
    )

    # Results
    winner_participant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='won_debates',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The participant who won the debate"
    )
    total_votes = models.IntegerField(default=0)

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='debate_sessions',
        through='Participation',
        blank=True
    )

    def __str__(self):
        return f"{self.topic.title} - {self.get_status_display()}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Debate Session'
        verbose_name_plural = 'Debate Sessions'

    def clean(self):
        """
        Validate session duration constraints.

        Raises:
            ValidationError: If duration is outside allowed range (20-180 minutes).
        """
        if self.duration_minutes < 20:
            raise ValidationError('Duration must be at least 20 minutes')
        if self.duration_minutes > 180:
            raise ValidationError('Duration cannot exceed 180 minutes')

    @property
    def is_voting_active(self):
        """
        Check if voting is currently active.

        Returns:
            bool: True if session is in voting phase.
        """
        return self.status == 'voting'

    @property
    def can_join_as_participant(self):
        """Check if new participants can join (only during 5-min joining window)"""
        return self.status == 'open'

    @property
    def can_join_as_viewer(self):
        """Check if users can join as viewers"""
        return self.status in ['closed', 'online', 'voting']

    @property
    def has_active_participants(self):
        """Check if there are active participants in the debate"""
        return self.participation_set.filter(
            role='participant',
            user__is_active=True
        ).exists()

    @property
    def active_participants_count(self):
        """Count of active participants currently in debate"""
        return self.participation_set.filter(
            role='participant',
            user__is_active=True
        ).count()

    @property
    def viewers_count(self):
        """Count of viewers in the session"""
        return self.participation_set.filter(role='viewer').count()

    def start_joining_window(self):
        """Start the 5-minute joining window"""
        if self.status != 'offline':
            raise ValidationError("Can only start joining window from offline status")

        now = timezone.now()
        self.status = 'open'
        self.joining_started_at = now
        self.joining_window_end = now + timedelta(minutes=5)
        self.save()

    def close_joining_window(self):
        """Close joining window and allow only viewers"""
        if self.status != 'open':
            raise ValidationError("Can only close from open status")

        self.status = 'closed'
        self.save()

        # Convert late joiners to viewers
        self.participation_set.filter(
            joined_at__gt=self.joining_window_end
        ).update(role='viewer')

    def start_debate(self):
        """Start the actual debate (unlock chat for participants)"""
        if self.status not in ['open', 'closed']:
            raise ValidationError("Can only start debate from open or closed status")

        now = timezone.now()
        self.status = 'online'
        self.debate_started_at = now
        self.debate_end_time = now + timedelta(minutes=self.duration_minutes)
        self.save()

    def end_debate_and_start_voting(self):
        """End debate and start 30-second voting period"""
        if self.status != 'online':
            raise ValidationError("Can only end debate from online status")

        now = timezone.now()
        self.status = 'voting'
        self.voting_started_at = now
        self.voting_end_time = now + timedelta(seconds=30)
        self.save()

    def finish_voting(self):
        """End voting and calculate side-based results"""
        if self.status != 'voting':
            raise ValidationError("Can only finish from voting status")

        # Calculate side-based winner
        from django.db.models import Count
        votes = self.votes.values('vote').annotate(
            vote_count=Count('vote')
        ).order_by('-vote_count')

        proposition_votes = 0
        opposition_votes = 0

        for vote_data in votes:
            if vote_data['vote'] == 'proposition':
                proposition_votes = vote_data['vote_count']
            elif vote_data['vote'] == 'opposition':
                opposition_votes = vote_data['vote_count']

        # Determine winner
        if proposition_votes > opposition_votes:
            # Find a proposition participant to declare winner
            winner_participation = self.participation_set.filter(
                role='participant', side='proposition'
            ).first()
            if winner_participation:
                self.winner_participant = winner_participation.user
        elif opposition_votes > proposition_votes:
            # Find an opposition participant to declare winner
            winner_participation = self.participation_set.filter(
                role='participant', side='opposition'
            ).first()
            if winner_participation:
                self.winner_participant = winner_participation.user
        # If tie, winner_participant remains None

        self.total_votes = proposition_votes + opposition_votes
        self.status = 'finished'
        self.save()

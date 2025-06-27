"""
DebateSession model for managing debate sessions and their lifecycle.
"""

from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .topic_models import DebateTopic


class DebateSession(models.Model):
    STATUS_CHOICES = [
        ('offline', 'Offline'),     # Not started yet - moderator hasn't opened joining
        ('open', 'Open'),           # 5-min joining window active - participants can join
        ('closed', 'Closed'),       # Joining window closed - only viewers can join
        ('online', 'Online'),       # Debate active - chat unlocked for participants
        ('voting', 'Voting'),       # Debate ended - 30-second voting period
        ('finished', 'Finished'),   # Voting ended - results calculated
        ('cancelled', 'Cancelled'),  # Session cancelled by moderator
    ]

    topic = models.ForeignKey(
        DebateTopic,
        on_delete=models.CASCADE,
        related_name='sessions')
    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='moderated_sessions',
        on_delete=models.SET_NULL,
        null=True
    )

    # Scheduling and Duration
    scheduled_start = models.DateTimeField(null=True, blank=True)  # Optional scheduling
    duration_minutes = models.IntegerField(
        default=60,
        help_text="Debate duration in minutes (20-180)"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')

    # Session lifecycle timestamps
    joining_started_at = models.DateTimeField(
        null=True, blank=True)  # When joining window opened (5 min)
    joining_window_end = models.DateTimeField(
        null=True, blank=True)  # When joining window closes
    debate_started_at = models.DateTimeField(
        null=True, blank=True)   # When debate chat unlocked
    debate_end_time = models.DateTimeField(
        null=True, blank=True)     # When debate will/did end
    voting_started_at = models.DateTimeField(
        null=True, blank=True)   # When 30-sec voting started
    voting_end_time = models.DateTimeField(
        null=True, blank=True)     # When voting ended

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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.topic.title} - {self.get_status_display()}"

    def clean(self):
        """Validate session duration"""
        if self.duration_minutes < 20:
            raise ValidationError('Duration must be at least 20 minutes')
        if self.duration_minutes > 180:
            raise ValidationError('Duration cannot exceed 180 minutes')

    @property
    def is_voting_active(self):
        """Check if voting is currently active (30-second window)"""
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

    @property
    def participant_count(self):
        """Get count of active participants"""
        return self.participation_set.filter(role='participant').count()

    @property
    def viewer_count(self):
        """Get count of viewers"""
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

        self.total_votes = proposition_votes + opposition_votes

        # Determine winning side and update participant stats
        if proposition_votes > opposition_votes:
            winning_side = 'proposition'
        elif opposition_votes > proposition_votes:
            winning_side = 'opposition'
        else:
            winning_side = 'tie'

        # Update win counts for participants on winning side
        if winning_side != 'tie':
            from .profile_models import UserProfile
            winning_participants = self.participation_set.filter(
                role='participant',
                side=winning_side
            ).select_related('user__debate_profile')

            for participation in winning_participants:
                profile, created = UserProfile.objects.get_or_create(
                    user=participation.user
                )
                profile.total_debates_won += 1
                profile.save()

        # Update total debates for all participants
        from .profile_models import UserProfile
        all_participants = self.participation_set.filter(
            role='participant'
        ).select_related('user__debate_profile')

        for participation in all_participants:
            profile, created = UserProfile.objects.get_or_create(
                user=participation.user
            )
            profile.total_debates_participated += 1
            profile.save()

        self.status = 'finished'
        self.save()

        return {
            'winning_side': winning_side,
            'proposition_votes': proposition_votes,
            'opposition_votes': opposition_votes,
            'total_votes': self.total_votes
        }

    class Meta:
        ordering = ['-created_at']

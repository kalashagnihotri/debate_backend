"""
Participation model for managing user participation in debate sessions.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .session_models import DebateSession


class Participation(models.Model):
    ROLE_CHOICES = [
        ('participant', 'Participant'),
        ('viewer', 'Viewer'),
    ]

    SIDE_CHOICES = [
        ('proposition', 'Proposition'),
        ('opposition', 'Opposition'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session = models.ForeignKey(DebateSession, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    side = models.CharField(max_length=20, choices=SIDE_CHOICES, null=True, blank=True,
                            help_text="Which side the participant is debating for (only for participants)")

    joined_at = models.DateTimeField(default=timezone.now)
    is_muted = models.BooleanField(default=False)
    warnings_count = models.IntegerField(default=0)
    messages_sent = models.IntegerField(default=0)
    has_voted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'session')

    def __str__(self):
        side_text = f" ({self.side})" if self.side else ""
        return f"{self.user.username} - {self.role}{side_text} in {self.session}"

    def clean(self):
        """Validate that participants must choose a side"""
        if self.role == 'participant' and not self.side:
            raise ValidationError(
                "Participants must choose a side (proposition or opposition)")
        if self.role == 'viewer' and self.side:
            raise ValidationError("Viewers cannot choose a side")

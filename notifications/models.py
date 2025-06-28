from django.conf import settings
from django.db import models
from django.utils import timezone


class Notification(models.Model):
    """
    Model representing notifications sent to users.
    
    As per requirements:
    - id (Primary Key)
    - user (ForeignKey to User model)
    - title (CharField for notification title)
    - message (TextField)
    - type (ChoiceField: UPCOMING_DEBATE, SESSION_CHANGE, MODERATION_ACTION)
    - notification_type (alias for type field)
    - is_read (BooleanField, default=False)
    - created_at (Timestamp)
    """
    
    # Required notification types as per specifications
    TYPE_CHOICES = [
        ('UPCOMING_DEBATE', 'Upcoming Debate'),
        ('SESSION_CHANGE', 'Session Change'),
        ('MODERATION_ACTION', 'Moderation Action'),
        ('debate_starting', 'Debate Starting'),
        ('debate_started', 'Debate Started'),
        ('debate_ended', 'Debate Ended'),
        ('debate_invitation', 'Debate Invitation'),
        ('session_invite', 'Session Invite'),
        ('moderation_action', 'Moderation Action'),
        ('vote_reminder', 'Vote Reminder'),
        ('session_starting', 'Session Starting'),
        ('joining_opened', 'Joining Opened'),
        ('joining_closing', 'Joining Closing'),
        ('voting_started', 'Voting Started'),
        ('session_finished', 'Session Finished'),
        ('debate_reminder', 'Debate Reminder'),
    ]
    
    # Required fields as per specifications
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="The user who will receive this notification"
    )
    title = models.CharField(
        max_length=255,
        help_text="The notification title",
        default="Notification"
    )
    message = models.TextField(
        help_text="The notification message content"
    )
    type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        help_text="Type of notification"
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Whether the notification has been read"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the notification was created"
    )

    def __init__(self, *args, **kwargs):
        # Handle notification_type as alias for type
        if 'notification_type' in kwargs:
            kwargs['type'] = kwargs.pop('notification_type')
        super().__init__(*args, **kwargs)

    @property
    def notification_type(self):
        """Alias for type field for backward compatibility."""
        return self.type

    @notification_type.setter
    def notification_type(self, value):
        """Setter for notification_type alias."""
        self.type = value

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['type']),
        ]

    def __str__(self):
        return f"{self.get_type_display()} -> {self.user.username}"

    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])


class NotificationPreference(models.Model):
    """User preferences for notifications"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )

    # Notification type preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    debate_start_notifications = models.BooleanField(default=True)
    voting_notifications = models.BooleanField(default=True)
    moderator_action_notifications = models.BooleanField(default=True)

    # Timing preferences
    notification_frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediate', 'Immediate'),
            ('hourly', 'Hourly Digest'),
            ('daily', 'Daily Digest'),
        ],
        default='immediate'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification preferences for {self.user.username}"

    class Meta:
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
"""
User models for the debate platform.

This module contains custom user model with role-based functionality
and extended user profiles for debate-specific data.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model with role-based functionality.

    Extends Django's AbstractUser to add debate-specific roles
    and computed properties for user statistics.
    """

    ROLE_CHOICES = [
        ('student', 'Student'),
        ('moderator', 'Moderator'),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student',
        help_text="User role determining platform permissions"
    )

    def __str__(self):
        """Return string representation of user."""
        return self.username

    @property
    def total_debates_participated(self):
        """
        Count total debates this user has participated in.

        Returns:
            int: Number of debates where user was an active participant
        """
        from debates.models import Participation
        return Participation.objects.filter(
            user=self,
            role='participant'
        ).count()

    @property
    def total_debates_won(self):
        """
        Count total debates this user has won.

        Note: Currently returns 0 as the voting system doesn't track
        individual winners. This could be enhanced in the future to
        determine winners based on debate sides and voting outcomes.

        Returns:
            int: Number of debates won (currently always 0)
        """
        return 0

    @property
    def total_messages_sent(self):
        """
        Count total messages sent by this user.

        Returns:
            int: Number of messages authored by this user
        """
        from debates.models import Message
        return Message.objects.filter(user=self).count()


class Profile(models.Model):
    """
    Extended user profile for debate-specific information.

    Stores additional user data like bio, profile picture, and activity tracking.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        help_text="One-to-one relationship with User model"
    )
    bio = models.TextField(
        blank=True,
        null=True,
        help_text="User biography or description"
    )
    profile_picture = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="URL to user profile picture"
    )
    date_joined = models.DateTimeField(
        auto_now_add=True,
        help_text="When the profile was created"
    )
    last_active = models.DateTimeField(
        auto_now=True,
        help_text="Last time the user was active"
    )

    class Meta:
        """Meta options for Profile model."""
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['-last_active']

    def __str__(self):
        """Return string representation of profile."""
        return f"{self.user.username}'s Profile"

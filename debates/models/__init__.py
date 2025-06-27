"""
Models package for debates app.
Exports all models for use throughout the application.
"""

# Import base classes for other apps that might need them
from .base import StatusMixin, TimestampedMixin
from .message import Message
from .moderation import ModerationAction, SessionTranscript, UserProfile
from .participation import Participation
from .session import DebateSession
from .topic import DebateTopic
from .vote import Vote, DebateVote

# Import notification models from the notifications app
try:
    from notifications.models import Notification
except ImportError:
    # Fallback if notifications app is not available
    Notification = None

__all__ = [
    # Core models
    'DebateTopic',
    'DebateSession',
    'Participation',
    'Message',
    'Vote',
    'DebateVote',  # For backward compatibility
    'ModerationAction',
    'UserProfile',
    'SessionTranscript',
    'Notification',

    # Base classes
    'TimestampedMixin',
    'StatusMixin',
]

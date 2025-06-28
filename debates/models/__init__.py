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

    # Base classes
    'TimestampedMixin',
    'StatusMixin',
]

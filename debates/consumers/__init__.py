"""
Consumers package for debates app.
Exports all consumers for use in routing.
"""

from .debate_consumer import DebateConsumer
from .notification_consumer import NotificationConsumer

__all__ = [
    'NotificationConsumer',
    'DebateConsumer',
]

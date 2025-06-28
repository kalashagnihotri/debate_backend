"""
Consumers for the debates app - now using modular structure.
This file imports all consumers from the consumers package for backward compatibility.
"""

# Import all consumers from the modular structure
from .consumers import DebateConsumer, NotificationConsumer

__all__ = ["DebateConsumer", "NotificationConsumer"]

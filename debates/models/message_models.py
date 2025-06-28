"""
Message model for handling debate session messages.
"""

from django.conf import settings
from django.db import models

from .session_models import DebateSession


class Message(models.Model):
    MESSAGE_TYPE_CHOICES = [
        ("text", "Text Message"),
        ("system", "System Message"),
        ("join", "User Joined"),
        ("leave", "User Left"),
        ("image", "Image Message"),
    ]

    session = models.ForeignKey(
        DebateSession, related_name="messages", on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )  # Null for system messages
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    message_type = models.CharField(
        max_length=20, choices=MESSAGE_TYPE_CHOICES, default="text"
    )

    # For image messages
    image_url = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        if self.author:
            return f"{self.author.username}: {self.content[:50]}"
        return f"System: {self.content[:50]}"

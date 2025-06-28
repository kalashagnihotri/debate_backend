"""
Topic model for debates.
"""

from django.db import models
from django.contrib.auth import get_user_model

from .base import TimestampedMixin

User = get_user_model()


class DebateTopic(TimestampedMixin):
    CATEGORY_CHOICES = [
        ("politics", "Politics"),
        ("technology", "Technology"),
        ("education", "Education"),
        ("environment", "Environment"),
        ("healthcare", "Healthcare"),
        ("economics", "Economics"),
        ("social", "Social Issues"),
        ("science", "Science"),
        ("entertainment", "Entertainment"),
        ("sports", "Sports"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default="other"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_topics",
        help_text="The moderator who created this topic",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Debate Topic"
        verbose_name_plural = "Debate Topics"

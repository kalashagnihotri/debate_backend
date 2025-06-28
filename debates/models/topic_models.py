"""
DebateTopic model for managing debate topics and categories.
"""

from django.db import models


class DebateTopic(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]

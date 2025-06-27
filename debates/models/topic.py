"""
Topic model for debates.
"""

from django.db import models

from .base import TimestampedMixin


class DebateTopic(TimestampedMixin):
    CATEGORY_CHOICES = [
        ('politics', 'Politics'),
        ('technology', 'Technology'),
        ('education', 'Education'),
        ('environment', 'Environment'),
        ('healthcare', 'Healthcare'),
        ('economics', 'Economics'),
        ('social', 'Social Issues'),
        ('science', 'Science'),
        ('entertainment', 'Entertainment'),
        ('sports', 'Sports'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Debate Topic'
        verbose_name_plural = 'Debate Topics'

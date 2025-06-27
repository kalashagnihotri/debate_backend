"""
Debates application configuration.

This module contains the Django app configuration for the debates application,
which handles debate sessions, topics, messaging, and related functionality.
"""

from django.apps import AppConfig


class DebatesConfig(AppConfig):
    """
    Configuration class for the Debates Django application.

    This app handles the core debate functionality including sessions,
    topics, messages, voting, and moderation features.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'debates'
    verbose_name = 'Debate Management'

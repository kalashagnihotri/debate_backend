"""
Users application configuration.

This module contains the Django app configuration for the users application,
which handles user authentication, profiles, and user management functionality.
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Configuration class for the Users Django application.

    This app handles user authentication, registration, profiles,
    and user-related functionality for the debate platform.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

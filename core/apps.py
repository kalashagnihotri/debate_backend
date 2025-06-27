"""
Core application configuration.

This module contains the Django app configuration for the core application,
which provides shared functionality across the debate platform.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Configuration class for the Core Django application.

    This app provides shared functionality including permissions,
    services, and base components used across the debate platform.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Core Application'

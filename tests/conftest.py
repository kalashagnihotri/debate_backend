"""
Test configuration for the Django debate platform.

This module provides test settings and configurations for running
the complete test suite.
"""

import os
import sys
import pytest
from pathlib import Path
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set the Django settings module for tests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlineDebatePlatform.test_settings')

import django
django.setup()

from debates.models import DebateTopic, DebateSession
from notifications.models import Notification

User = get_user_model()


@pytest.fixture
def api_client():
    """Provide an API client for testing."""
    return APIClient()


@pytest.fixture
def test_user(db):
    """Create a test student user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='TestPassword123!',
        role='student'
    )


@pytest.fixture
def test_moderator(db):
    """Create a test moderator user."""
    return User.objects.create_user(
        username='testmoderator',
        email='moderator@example.com',
        password='ModeratorPassword123!',
        role='moderator'
    )


@pytest.fixture
def authenticated_client(api_client, test_user):
    """Provide an authenticated API client for student."""
    refresh = RefreshToken.for_user(test_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def moderator_client(api_client, test_moderator):
    """Provide an authenticated API client for moderator."""
    refresh = RefreshToken.for_user(test_moderator)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def test_topic(test_moderator):
    """Create a test debate topic."""
    return DebateTopic.objects.create(
        title='Test Topic',
        description='A test debate topic for testing purposes',
        category='Education',
        created_by=test_moderator
    )


@pytest.fixture
def test_session(test_topic, test_moderator):
    """Create a test debate session."""
    return DebateSession.objects.create(
        topic=test_topic,
        moderator=test_moderator,
        scheduled_start=timezone.now() + timezone.timedelta(hours=1),
        duration_minutes=60,
        status='scheduled'
    )


@pytest.fixture
def active_session(test_topic, test_moderator):
    """Create an active debate session."""
    return DebateSession.objects.create(
        topic=test_topic,
        moderator=test_moderator,
        scheduled_start=timezone.now() - timezone.timedelta(minutes=30),
        duration_minutes=60,
        status='online'
    )


@pytest.fixture
def test_notification(test_user):
    """Create a test notification."""
    return Notification.objects.create(
        user=test_user,
        title='Test Notification',
        message='This is a test notification',
        notification_type='debate_reminder'
    )


@pytest.fixture
def multiple_users(db):
    """Create multiple test users."""
    users = []
    for i in range(5):
        user = User.objects.create_user(
            username=f'testuser{i}',
            email=f'testuser{i}@example.com',
            password='TestPassword123!',
            role='student'
        )
        users.append(user)
    return users


@pytest.fixture
def multiple_topics(test_moderator):
    """Create multiple test topics."""
    topics = []
    categories = ['Education', 'Technology', 'Politics', 'Science', 'Sports']
    for i, category in enumerate(categories):
        topic = DebateTopic.objects.create(
            title=f'Test Topic {i+1}',
            description=f'Description for test topic {i+1}',
            category=category,
            created_by=test_moderator
        )
        topics.append(topic)
    return topics


# Pytest configuration
def pytest_configure(config):
    """Configure pytest for Django testing."""
    import django
    from django.conf import settings
    if not settings.configured:
        django.setup()


# Custom markers for test categorization
pytest_plugins = []


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Add slow marker to performance tests
        if 'performance' in item.nodeid.lower() or 'concurrent' in item.nodeid.lower():
            item.add_marker(pytest.mark.slow)
        
        # Add integration marker to integration tests
        if 'integration' in item.nodeid.lower() or 'workflow' in item.nodeid.lower():
            item.add_marker(pytest.mark.integration)
        
        # Add unit marker to unit tests
        if 'test_' in item.name and 'integration' not in item.nodeid.lower():
            item.add_marker(pytest.mark.unit)

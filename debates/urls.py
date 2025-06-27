"""
URL routing for the debates app.

This module defines all URL patterns for debate-related API endpoints,
including topics, sessions, messages, votes, notifications, and moderation.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DebateSessionViewSet,
    DebateTopicViewSet,
    DebateVoteViewSet,
    MessageViewSet,
    ModerationActionViewSet,
    SessionTranscriptViewSet,
    UserProfileViewSet,
)

# Create router and register all viewsets
router = DefaultRouter()
router.register(r'topics', DebateTopicViewSet, basename='topic')
router.register(r'sessions', DebateSessionViewSet, basename='session')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'votes', DebateVoteViewSet, basename='vote')
router.register(r'profiles', UserProfileViewSet, basename='profile')
router.register(r'transcripts', SessionTranscriptViewSet, basename='transcript')
router.register(
    r'moderation-actions',
    ModerationActionViewSet,
    basename='moderation-action'
)

urlpatterns = [
    path('', include(router.urls)),
]

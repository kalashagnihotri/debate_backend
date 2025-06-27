# Performance Optimization for Django Online Debate Platform
# This file contains optimized view methods and caching strategies

import json
from datetime import timedelta

from django.core.cache import cache
from django.db.models import Count, Prefetch, Q
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.decorators import action
from rest_framework.response import Response

# Import models
from ..models import (
    DebateSession,
    DebateTopic,
    DebateVote,
    Message,
    Notification,
    Participation,
)


# Mixin for adding performance optimizations to views
class PerformanceOptimizedMixin:
    """
    Mixin to add performance optimizations to ViewSets
    """

    def get_queryset(self):
        """Optimize querysets with select_related and prefetch_related"""
        queryset = super().get_queryset()

        # For DebateSessionViewSet
        if hasattr(self, 'serializer_class') and 'DebateSession' in str(
                self.serializer_class):
            queryset = queryset.select_related(
                'topic', 'moderator'
            ).prefetch_related(
                Prefetch(
                    'participation_set',
                    queryset=Participation.objects.select_related('user')),
                Prefetch('messages', queryset=Message.objects.select_related(
                    'author').order_by('-timestamp')[:50]),
                'votes__voter'
            )

        # For DebateTopicViewSet
        elif hasattr(self, 'serializer_class') and 'DebateTopic' in str(self.serializer_class):
            queryset = queryset.annotate(
                session_count=Count('sessions'),
                active_session_count=Count(
                    'sessions', filter=Q(
                        sessions__status__in=[
                            'scheduled', 'joining', 'active']))
            )

        return queryset

    def get_cached_data(self, cache_key, cache_timeout=300):
        """Generic method to get cached data"""
        return cache.get(cache_key)

    def set_cached_data(self, cache_key, data, cache_timeout=300):
        """Generic method to set cached data"""
        cache.set(cache_key, data, cache_timeout)
        return data

# Optimized debate session statistics


def get_session_statistics(session_id, use_cache=True):
    """Get comprehensive session statistics with caching"""
    cache_key = f"session_stats_{session_id}"

    if use_cache:
        cached_stats = cache.get(cache_key)
        if cached_stats:
            return cached_stats

    try:
        session = DebateSession.objects.select_related(
            'topic', 'moderator').get(id=session_id)

        # Get participant statistics
        participants = session.participation_set.select_related('user').all()
        participant_stats = {
            'total_participants': participants.count(),
            'active_participants': participants.filter(role='participant').count(),
            'viewers': participants.filter(role='viewer').count(),
            'muted_users': participants.filter(is_muted=True).count(),
        }

        # Get message statistics
        message_stats = {
            'total_messages': session.messages.count(),
            'recent_messages': session.messages.filter(
                timestamp__gte=timezone.now() - timedelta(minutes=30)
            ).count(),
        }

        # Get voting statistics
        vote_stats = {
            'total_votes': session.votes.count(),
            'vote_distribution': dict(
                session.votes.values('vote').annotate(
                    count=Count('vote')).values_list(
                    'vote', 'count')
            )
        }

        stats = {
            'session_id': session_id,
            'status': session.status,
            'participants': participant_stats,
            'messages': message_stats,
            'votes': vote_stats,
            'last_updated': timezone.now().isoformat(),
        }

        # Cache for 5 minutes
        if use_cache:
            cache.set(cache_key, stats, 300)

        return stats

    except DebateSession.DoesNotExist:
        return None

# Database query optimization functions


def get_popular_topics(limit=10):
    """Get popular topics with session count"""
    cache_key = "popular_topics"
    cached_topics = cache.get(cache_key)

    if cached_topics:
        return cached_topics

    topics = DebateTopic.objects.annotate(
        session_count=Count('sessions'),
        recent_session_count=Count(
            'sessions',
            filter=Q(sessions__created_at__gte=timezone.now() - timedelta(days=30))
        )
    ).order_by('-session_count', '-recent_session_count')[:limit]

    # Cache for 1 hour
    cache.set(cache_key, list(topics.values()), 3600)
    return topics


def get_active_sessions_optimized():
    """Get active sessions with optimized queries"""
    cache_key = "active_sessions"
    cached_sessions = cache.get(cache_key)

    if cached_sessions:
        return cached_sessions

    sessions = DebateSession.objects.filter(
        status__in=['scheduled', 'joining', 'active', 'voting']
    ).select_related('topic', 'moderator').prefetch_related(
        'participation_set__user',
        'messages__author'
    ).annotate(
        participant_count=Count(
            'participation_set', filter=Q(
                participation_set__role='participant')),
        viewer_count=Count(
            'participation_set', filter=Q(
                participation_set__role='viewer')),
        message_count=Count('messages')
    ).order_by('scheduled_start')

    # Cache for 2 minutes (short cache for active data)
    cache.set(cache_key, list(sessions.values()), 120)
    return sessions


def get_user_session_history(user_id, limit=20):
    """Get user's session history with optimized queries"""
    cache_key = f"user_history_{user_id}"
    cached_history = cache.get(cache_key)

    if cached_history:
        return cached_history

    participations = Participation.objects.filter(
        user_id=user_id
    ).select_related(
        'session__topic', 'session__moderator'
    ).order_by('-joined_at')[:limit]

    history = []
    for participation in participations:
        history.append({
            'session_id': participation.session.id,
            'topic_title': participation.session.topic.title,
            'role': participation.role,
            'joined_at': participation.joined_at,
            'status': participation.session.status,
            'messages_sent': participation.messages_sent,
            'has_voted': participation.has_voted,
        })

    # Cache for 10 minutes
    cache.set(cache_key, history, 600)
    return history

# Cache invalidation helpers


def invalidate_session_cache(session_id):
    """Invalidate all cache entries related to a session"""
    cache_keys = [
        f"session_stats_{session_id}",
        "active_sessions",
        "popular_topics",
    ]
    cache.delete_many(cache_keys)


def invalidate_user_cache(user_id):
    """Invalidate cache entries related to a user"""
    cache_keys = [
        f"user_history_{user_id}",
    ]
    cache.delete_many(cache_keys)

# Batch operations for better performance


def bulk_create_notifications(notifications_data):
    """Bulk create notifications for better performance"""
    notifications = [
        Notification(**data) for data in notifications_data
    ]
    return Notification.objects.bulk_create(notifications, batch_size=100)


def bulk_update_participations(participations, fields):
    """Bulk update participations"""
    return Participation.objects.bulk_update(participations, fields, batch_size=100)

# Performance monitoring decorators


def monitor_query_count(func):
    """Decorator to monitor database query count"""
    def wrapper(*args, **kwargs):
        from django.db import connection
        initial_queries = len(connection.queries)

        result = func(*args, **kwargs)

        final_queries = len(connection.queries)
        query_count = final_queries - initial_queries

        # Log if too many queries
        if query_count > 10:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"High query count in {
                    func.__name__}: {query_count} queries")

        return result
    return wrapper

# Redis-based real-time data caching (if Redis is available)


def get_real_time_session_data(session_id):
    """Get real-time session data with Redis fallback"""
    try:
        import redis
        redis_client = redis.Redis(host='localhost', port=6379, db=0)

        # Try to get from Redis first
        redis_key = f"session_realtime_{session_id}"
        cached_data = redis_client.get(redis_key)

        if cached_data:
            return json.loads(cached_data)
    except (ImportError, ConnectionError):
        pass  # Redis not available, fall back to Django cache

    # Fallback to Django cache
    return cache.get(f"session_realtime_{session_id}")


def set_real_time_session_data(session_id, data, expire_seconds=60):
    """Set real-time session data with Redis fallback"""
    try:
        import redis
        redis_client = redis.Redis(host='localhost', port=6379, db=0)

        redis_key = f"session_realtime_{session_id}"
        redis_client.setex(redis_key, expire_seconds, json.dumps(data))
        return True
    except (ImportError, ConnectionError):
        pass  # Redis not available, fall back to Django cache

    # Fallback to Django cache
    cache.set(f"session_realtime_{session_id}", data, expire_seconds)
    return True

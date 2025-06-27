from debates.models import DebateSession, Message, Participation
from debates.serializers import DebateSessionSerializer
from django.core.cache import cache
from django.db.models import Count, Prefetch, Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.decorators import action
from rest_framework.response import Response


class OptimizedDebateSessionViewSet:
    """
    Performance-optimized methods for DebateSessionViewSet
    These can be integrated into the main views.py file
    """

    def get_queryset(self):
        """Optimized queryset with select_related and prefetch_related"""
        return DebateSession.objects.select_related(
            'topic', 'moderator'
        ).prefetch_related(
            Prefetch(
                'participation_set',
                queryset=Participation.objects.select_related('user')
            ),
            Prefetch(
                'messages',
                queryset=Message.objects.select_related(
                    'author').order_by('-timestamp')[:20]
            ),
            'votes__voter'
        ).annotate(
            participant_count=Count(
                'participation_set', filter=Q(
                    participation_set__role='participant')),
            viewer_count=Count(
                'participation_set', filter=Q(
                    participation_set__role='viewer')),
            message_count=Count('messages')
        )

    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def list(self, request):
        """Cached list view for sessions"""
        queryset = self.get_queryset()
        serializer = DebateSessionSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get cached session statistics"""
        cache_key = f"session_stats_{pk}"
        stats = cache.get(cache_key)

        if not stats:
            session = self.get_object()
            stats = {
                'total_participants': session.participation_set.count(),
                'active_participants': session.participation_set.filter(role='participant').count(),
                'viewers': session.participation_set.filter(role='viewer').count(),
                'total_messages': session.messages.count(),
                'total_votes': session.votes.count(),
                'status': session.status,
                'duration_minutes': session.duration_minutes,
            }
            # Cache for 2 minutes
            cache.set(cache_key, stats, 120)

        return Response(stats)

    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular sessions with caching"""
        cache_key = "popular_sessions"
        popular_sessions = cache.get(cache_key)

        if not popular_sessions:
            sessions = self.get_queryset().filter(
                participant_count__gt=0
            ).order_by('-participant_count', '-message_count')[:10]

            serializer = DebateSessionSerializer(sessions, many=True)
            popular_sessions = serializer.data

            # Cache for 10 minutes
            cache.set(cache_key, popular_sessions, 600)

        return Response(popular_sessions)

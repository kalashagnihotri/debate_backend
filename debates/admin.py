"""
Django admin configuration for debates app.

Provides comprehensive admin interface for all debate-related models
including topics, sessions, messages, participation, moderation, votes,
user profiles, and session transcripts.
"""

from django.contrib import admin

from .models import (
    DebateSession,
    DebateTopic,
    Message,
    ModerationAction,
    Participation,
    SessionTranscript,
    UserProfile,
    Vote,
)


@admin.register(DebateTopic)
class DebateTopicAdmin(admin.ModelAdmin):
    """Admin interface for debate topics."""

    list_display = ("title", "category", "created_at", "updated_at")
    list_filter = ("category", "created_at")
    search_fields = ("title", "description")


@admin.register(DebateSession)
class DebateSessionAdmin(admin.ModelAdmin):
    """Admin interface for debate sessions."""

    list_display = (
        "topic",
        "moderator",
        "status",
        "scheduled_start",
        "debate_started_at",
        "debate_end_time",
    )
    list_filter = ("status", "scheduled_start", "debate_started_at")
    search_fields = ("topic__title", "moderator__username")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin interface for debate messages."""

    list_display = ("session", "user", "content", "timestamp", "message_type")
    list_filter = ("message_type", "timestamp")
    search_fields = ("content", "user__username")


@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    """Admin interface for session participation."""

    list_display = (
        "session",
        "user",
        "role",
        "joined_at",
        "is_muted",
        "warnings_count",
    )
    list_filter = ("role", "is_muted", "joined_at")
    search_fields = ("user__username", "session__topic__title")


@admin.register(ModerationAction)
class ModerationActionAdmin(admin.ModelAdmin):
    """Admin interface for moderation actions."""

    list_display = ("session", "moderator", "target_user", "action", "timestamp")
    list_filter = ("action", "timestamp")
    search_fields = ("moderator__username", "target_user__username")


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    """Admin interface for votes."""

    list_display = ("debate_session", "user", "vote_type", "created_at")
    list_filter = ("vote_type", "created_at")
    search_fields = ("user__username", "debate_session__topic__title")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for user profiles."""

    list_display = ("user", "reputation_score")
    search_fields = ("user__username",)


@admin.register(SessionTranscript)
class SessionTranscriptAdmin(admin.ModelAdmin):
    """Admin interface for session transcripts."""

    list_display = ("session", "generated_at")
    search_fields = ("session__topic__title",)

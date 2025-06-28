"""
Serializers for the debates app.

Provides serialization for all debate-related models, including topics, sessions, messages, participation, moderation, votes, notifications, and transcripts.
"""

from rest_framework import serializers
from users.serializers import UserSerializer

from .models import (
    DebateSession,
    DebateTopic,
    DebateVote,
    Message,
    ModerationAction,
    Participation,
    SessionTranscript,
    UserProfile,
    Vote,  # Add new Vote model
)


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for debate messages."""

    author = UserSerializer(read_only=True)
    session = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "session",
            "author",
            "content",
            "timestamp",
            "message_type",
            "image_url",
        ]


class DebateTopicSerializer(serializers.ModelSerializer):
    """Serializer for debate topics."""

    class Meta:
        model = DebateTopic
        fields = ["id", "title", "description", "category", "created_at", "updated_at"]


class ParticipationSerializer(serializers.ModelSerializer):
    """Serializer for session participation."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = Participation
        fields = [
            "user",
            "role",
            "joined_at",
            "is_muted",
            "warnings_count",
            "messages_sent",
            "has_voted",
        ]


class DebateSessionSerializer(serializers.ModelSerializer):
    """Serializer for debate sessions, including computed fields and related objects."""

    topic = DebateTopicSerializer(read_only=True)
    topic_id = serializers.IntegerField(write_only=True)
    moderator = UserSerializer(read_only=True)
    participants = ParticipationSerializer(
        source="participation_set", many=True, read_only=True
    )
    messages = MessageSerializer(many=True, read_only=True)
    winner_participant = UserSerializer(read_only=True)

    # Computed fields
    active_participants = serializers.SerializerMethodField()
    viewers = serializers.SerializerMethodField()
    can_join_as_participant = serializers.SerializerMethodField()
    can_join_as_viewer = serializers.SerializerMethodField()
    is_voting_active = serializers.SerializerMethodField()
    participant_count = serializers.SerializerMethodField()
    viewer_count = serializers.SerializerMethodField()
    has_active_participants = serializers.SerializerMethodField()

    class Meta:
        model = DebateSession
        fields = [
            "id",
            "topic",
            "topic_id",
            "moderator",
            "scheduled_start",
            "duration_minutes",
            "status",
            "joining_started_at",
            "joining_window_end",
            "debate_started_at",
            "debate_end_time",
            "voting_started_at",
            "voting_end_time",
            "winner_participant",
            "total_votes",
            "participants",
            "messages",
            "created_at",
            "updated_at",
            "active_participants",
            "viewers",
            "can_join_as_participant",
            "can_join_as_viewer",
            "is_voting_active",
            "participant_count",
            "viewer_count",
            "has_active_participants",
        ]
        read_only_fields = [
            "joining_started_at",
            "joining_window_end",
            "debate_started_at",
            "debate_end_time",
            "voting_started_at",
            "voting_end_time",
            "status",
            "winner_participant",
            "total_votes",
            "created_at",
            "updated_at",
        ]

    def get_active_participants(self, obj):
        """Return users who are active participants (not viewers)."""
        participants = obj.participation_set.filter(role="participant")
        return UserSerializer([p.user for p in participants], many=True).data

    def get_viewers(self, obj):
        """Return users who are viewers (not participants)."""
        viewers = obj.participation_set.filter(role="viewer")
        return UserSerializer([v.user for v in viewers], many=True).data

    def get_can_join_as_participant(self, obj):
        return obj.can_join_as_participant

    def get_can_join_as_viewer(self, obj):
        return obj.can_join_as_viewer

    def get_is_voting_active(self, obj):
        return obj.is_voting_active

    def get_participant_count(self, obj):
        return obj.participation_set.filter(role="participant").count()

    def get_viewer_count(self, obj):
        return obj.participation_set.filter(role="viewer").count()

    def get_has_active_participants(self, obj):
        return obj.has_active_participants


class ModerationActionSerializer(serializers.ModelSerializer):
    """Serializer for moderation actions taken during a session."""

    moderator = UserSerializer(read_only=True)
    target_user = UserSerializer(read_only=True)
    target_user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ModerationAction
        fields = [
            "id",
            "session",
            "moderator",
            "target_user",
            "target_user_id",
            "action",
            "reason",
            "timestamp",
        ]


class DebateVoteSerializer(serializers.ModelSerializer):
    """Serializer for votes cast in a debate session."""

    voter = UserSerializer(read_only=True)
    voted_for = UserSerializer(read_only=True)
    voted_for_id = serializers.IntegerField(write_only=True)
    best_argument_message = MessageSerializer(read_only=True)
    best_argument_message_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = DebateVote
        fields = [
            "id",
            "session",
            "voter",
            "voted_for",
            "voted_for_id",
            "best_argument_message",
            "best_argument_message_id",
            "timestamp",
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile and statistics."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "total_debates_participated",
            "total_debates_won",
            "total_messages_sent",
            "total_votes_cast",
            "reputation_score",
            "email_notifications",
            "created_at",
            "updated_at",
        ]


class SessionTranscriptSerializer(serializers.ModelSerializer):
    """Serializer for session transcripts."""

    session = DebateSessionSerializer(read_only=True)

    class Meta:
        model = SessionTranscript
        fields = ["id", "session", "content", "summary", "generated_at"]


class ParticipationDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for participation, used in admin or analytics."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = Participation
        fields = ["user", "is_muted", "role", "joined_at", "warnings_count"]


class VoteSerializer(serializers.ModelSerializer):
    """
    Serializer for individual votes in a debate.
    """

    user = UserSerializer(read_only=True)
    debate_session = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Vote
        fields = ["id", "user", "debate_session", "vote_type", "created_at"]
        read_only_fields = ["id", "created_at"]

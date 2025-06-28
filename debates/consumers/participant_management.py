"""
Participant management functionality for DebateConsumer.
"""

import logging

from channels.db import database_sync_to_async
from django.core.cache import cache

logger = logging.getLogger(__name__)


class ParticipantManagementMixin:
    """Mixin for managing participants in debate sessions"""

    @database_sync_to_async
    def add_participant(self):
        from ..models.message import Message  # Explicitly import from message.py
        from ..models.participation import Participation

        # Add user to active participants list in cache
        cache_key = f"debate_participants_{self.debate_id}"
        participants = cache.get(cache_key, [])

        # Check if user is not already in the list
        user_data = {
            "id": self.user.id,
            "username": self.user.username,
            "is_online": True,
        }

        # Remove existing entry if present (to avoid duplicates)
        participants = [p for p in participants if p["id"] != self.user.id]
        # Add current user
        participants.append(user_data)

        # Store back in cache (expire after 1 hour of inactivity)
        cache.set(cache_key, participants, 3600)

        # Create system message for user joining
        try:
            participation = Participation.objects.get(
                user=self.user, session=self.debate_session
            )
            role_text = participation.role.title()
        except Participation.DoesNotExist:
            role_text = "User"

        Message.objects.create(
            session=self.debate_session,
            user=None,  # System message - no user
            content=f"{self.user.username} joined as {role_text}",
            message_type="system",  # Changed from "join" to "system"
            is_system_message=True,  # Mark as system message
        )

        logger.info(
            f"Added participant {
                self.user.username} to debate {
                self.debate_id}. Total: {
                len(participants)}"
        )

    @database_sync_to_async
    def remove_participant(self):
        from ..models.message import Message  # Explicitly import from message.py
        from ..models.participation import Participation

        # Remove user from active participants list in cache
        cache_key = f"debate_participants_{self.debate_id}"
        participants = cache.get(cache_key, [])
        participants = [p for p in participants if p["id"] != self.user.id]
        cache.set(cache_key, participants, 3600)

        # Create system message for user leaving
        try:
            participation = Participation.objects.get(
                user=self.user, session=self.debate_session
            )
            role_text = participation.role.title()
        except Participation.DoesNotExist:
            role_text = "User"

        Message.objects.create(
            session=self.debate_session,
            user=None,  # System message - no user
            content=f"{self.user.username} ({role_text}) left the session",
            message_type="system",  # Changed from "leave" to "system"
            is_system_message=True,  # Mark as system message
        )

        logger.info(
            f"Removed participant {
                self.user.username} from debate {
                self.debate_id}. Remaining: {
                len(participants)}"
        )

    async def get_participants(self):
        # Get list of active participants from cache
        cache_key = f"debate_participants_{self.debate_id}"
        cached_participants = cache.get(cache_key, [])

        # Get moderation status from database for each participant
        participants_with_status = []
        for cached_participant in cached_participants:
            try:
                # Get participation data using async database call
                participation_data = await self.get_participation_data(
                    cached_participant["id"], self.debate_id
                )
                if participation_data:
                    participants_with_status.append(
                        {
                            "id": participation_data["user_id"],
                            "username": participation_data["username"],
                            "is_muted": participation_data["is_muted"],
                            "warnings_count": participation_data["warnings_count"],
                            "is_online": True,
                        }
                    )
                else:
                    # If no participation record exists, use cached data without
                    # moderation status
                    participants_with_status.append(
                        {
                            "id": cached_participant["id"],
                            "username": cached_participant["username"],
                            "is_muted": False,
                            "warnings_count": 0,
                            "is_online": True,
                        }
                    )
            except Exception as e:
                logger.error(
                    f"Error getting participation for user {
                        cached_participant['id']}: {e}"
                )
                # Fallback to cached data
                participants_with_status.append(
                    {
                        "id": cached_participant["id"],
                        "username": cached_participant["username"],
                        "is_muted": False,
                        "warnings_count": 0,
                        "is_online": True,
                    }
                )

        logger.info(
            f"Retrieved {
                len(participants_with_status)} participants for debate {
                self.debate_id}: {
                [
                    p['username'] for p in participants_with_status]}"
        )
        return participants_with_status

    @database_sync_to_async
    def get_participation_data(self, user_id, session_id):
        from ..models.participation import Participation

        try:
            participation = Participation.objects.select_related("user").get(
                user_id=user_id, session_id=session_id
            )
            return {
                "user_id": participation.user.id,
                "username": participation.user.username,
                "is_muted": participation.is_muted,
                "warnings_count": participation.warnings_count,
            }
        except Participation.DoesNotExist:
            return None

    @database_sync_to_async
    def cleanup_participants(self):
        """Clean up stale participant entries (optional periodic cleanup)"""
        cache_key = f"debate_participants_{self.debate_id}"
        participants = cache.get(cache_key, [])

        # For now, just return the current list
        # In the future, we could add logic to check for stale connections
        logger.info(
            f"Participant cleanup for debate {
                self.debate_id}: {
                len(participants)} active"
        )
        return participants

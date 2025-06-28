"""
Message handling functionality for DebateConsumer.
"""

import json
import logging
from datetime import datetime

from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class MessageHandlingMixin:
    """Mixin for handling debate messages"""

    async def handle_message(self, message_data):
        """Process incoming debate message"""
        message = message_data.get("message", "")
        emoji_reactions = message_data.get("emoji_reactions", {})
        image_url = message_data.get("image_url", "")

        # Check if user can send messages
        can_send = await self.can_user_send_message()
        if not can_send:
            await self.send_json(
                {"type": "error", "message": "You cannot send messages at this time"}
            )
            return

        # Save message to database
        await self.save_message(message, image_url)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "debate_message",
                "message": message,
                "user_id": self.user.id,
                "username": self.user.username,
                "timestamp": datetime.now().isoformat(),
                "emoji_reactions": emoji_reactions,
                "image_url": image_url,
            },
        )

    async def handle_typing(self, typing_data):
        """Handle typing indicators"""
        action = typing_data.get("action", "start")  # 'start' or 'stop'

        # Clear existing timeout if any
        if hasattr(self, "typing_timeout") and self.typing_timeout:
            self.typing_timeout.cancel()

        if action == "start":
            # Set timeout to auto-stop typing after 3 seconds
            import asyncio

            self.typing_timeout = asyncio.create_task(self.auto_stop_typing())

        # Broadcast typing status to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "typing_notification",
                "action": action,
                "user_id": self.user.id,
                "username": self.user.username,
            },
        )

    async def auto_stop_typing(self):
        """Auto-stop typing after timeout"""
        import asyncio

        await asyncio.sleep(3)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "typing_notification",
                "action": "stop",
                "user_id": self.user.id,
                "username": self.user.username,
            },
        )

    async def handle_reaction(self, reaction_data):
        """Handle message reactions"""
        message_id = reaction_data.get("message_id")
        emoji = reaction_data.get("emoji")

        if message_id and emoji:
            # Save reaction to database (implement if needed)
            # await self.save_reaction(message_id, emoji)

            # Broadcast reaction to room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "message_reaction",
                    "message_id": message_id,
                    "emoji": emoji,
                    "user_id": self.user.id,
                    "username": self.user.username,
                },
            )

    @database_sync_to_async
    def can_user_send_message(self):
        """Check if user can send messages"""
        from ..models import Participation

        try:
            # Check if user is muted
            participation = Participation.objects.get(
                user=self.user, session=self.debate_session
            )
            if participation.is_muted:
                return False

            # Check if session allows messaging (e.g., status is 'online')
            if self.debate_session.status != "online":
                return False

            # Check if user is a participant (only participants can send messages)
            if participation.role != "participant":
                return False

            return True
        except Participation.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content, image_url=None):
        """Save message to database"""
        from ..models import Message

        return Message.objects.create(
            session=self.debate_session,
            author=self.user,
            content=content,
            image_url=image_url or None,
            message_type="text",
        )

    # WebSocket event handlers
    async def debate_message(self, event):
        """Send message to WebSocket"""
        await self.send_json(
            {
                "type": "message",
                "message": event["message"],
                "user_id": event["user_id"],
                "username": event["username"],
                "timestamp": event.get("timestamp"),
                "emoji_reactions": event.get("emoji_reactions", {}),
                "image_url": event.get("image_url", ""),
            }
        )

    async def chat_message(self, event):
        """Broadcasting message from other consumers"""
        logger.info(f"Broadcasting message from {event['username']}")
        await self.send_json(
            {
                "type": "message",
                "message": event["message"],
                "username": event["username"],
                "user_id": event["user_id"],
                "timestamp": event["timestamp"],
                "image_url": event.get("image_url"),
                "emoji_reactions": event.get("emoji_reactions", {}),
            }
        )

    async def typing_notification(self, event):
        """Handle typing notifications"""
        # Don't send typing notification back to the sender
        if event.get("user_id") != getattr(self, "user", {}).id:
            await self.send_json(
                {
                    "type": "typing_notification",
                    "action": event["action"],
                    "user_id": event["user_id"],
                    "username": event["username"],
                }
            )

    async def message_reaction(self, event):
        """Handle message reactions"""
        await self.send_json(
            {
                "type": "message_reaction",
                "message_id": event["message_id"],
                "emoji": event["emoji"],
                "user_id": event["user_id"],
                "username": event["username"],
            }
        )

"""
Main WebSocket consumer for debate sessions.

This consumer handles all real-time WebSocket communication for debate sessions,
including user connections, message handling, participant management, and
session status updates.
"""

import logging
from datetime import datetime

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

from .base import BaseConsumerMixin
from .message_handling import MessageHandlingMixin
from .participant_management import ParticipantManagementMixin

User = get_user_model()
logger = logging.getLogger(__name__)


class DebateConsumer(
    BaseConsumerMixin,
    ParticipantManagementMixin,
    MessageHandlingMixin,
    AsyncWebsocketConsumer,
):
    """
    Main consumer for debate session WebSocket connections.

    Handles real-time communication including:
    - User authentication and connection management
    - Participant joining/leaving notifications
    - Message broadcasting and handling
    - Session status updates and moderation actions
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.typing_timeout = None

    async def connect(self):
        """
        Handle WebSocket connection establishment.

        Authenticates the user, validates session existence, and sets up
        the connection with proper room grouping and participant management.
        """
        logger.info("WebSocket connection attempt started")

        try:
            self.debate_id = self.scope["url_route"]["kwargs"]["debate_id"]
            self.room_group_name = f"debate_{self.debate_id}"

            logger.info(f"Debate ID: {self.debate_id}, Room: {self.room_group_name}")

            # Authenticate user
            user = await self.authenticate_connection()
            if not user:
                return

            logger.info(f"User authenticated: {user.username} (ID: {user.id})")

            # Check if debate session exists
            debate_session = await self.get_debate_session(self.debate_id)
            if not debate_session:
                logger.error(f"REJECT: Debate session {self.debate_id} not found")
                await self.close(code=4003)
                return

            logger.info(f"Debate session found: {debate_session.topic}")

            self.user = user
            self.debate_session = debate_session

            logger.info(f"Joining room group: {self.room_group_name}")

            # Join room group
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)

            logger.info(f"Accepting WebSocket connection for user: {user.username}")
            await self.accept()

            # Add user to participants and notify others
            await self.add_participant()

            # Send connection confirmation with current participants
            participants = await self.get_participants()
            logger.info(f"Sending connection confirmation to {user.username}")
            await self.send_json(
                {
                    "type": "connection_established",
                    "message": f"Connected to debate session {self.debate_id}",
                    "user_id": user.id,
                    "username": user.username,
                    "participants": participants,
                }
            )

            # Notify others that user joined
            logger.info(f"Notifying room that {user.username} joined")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_joined",
                    "user_id": self.user.id,
                    "username": self.user.username,
                    "participants": participants,
                },
            )

            # Send participant list update to all users (including self)
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "participant_update", "participants": participants},
            )
            logger.info(
                f"WebSocket connection completed successfully for user: "
                f"{user.username}"
            )

        except Exception as e:
            logger.error(f"Error during WebSocket connection: {e}")
            await self.close(code=1011)

    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.

        Removes the user from participants, notifies other users,
        and cleans up the connection properly.

        Args:
            close_code: The WebSocket close code.
        """
        logger.info(f"WebSocket disconnect initiated with code: {close_code}")

        # Remove user from participants and notify others
        if hasattr(self, "user"):
            logger.info(f"User {self.user.username} disconnecting")
            await self.remove_participant()
            participants = await self.get_participants()

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_left",
                    "user_id": self.user.id,
                    "username": self.user.username,
                    "participants": participants,
                },
            )

            # Send participant list update to all remaining users
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "participant_update", "participants": participants},
            )
        else:
            logger.warning("Disconnect called but no user was set")

        # Leave room group
        if hasattr(self, "room_group_name"):
            logger.info(f"Leaving room group: {self.room_group_name}")
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )

        logger.info("WebSocket disconnect completed")

    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages.

        Processes different message types including regular messages,
        typing indicators, reactions, and ping/pong for connection stability.

        Args:
            text_data: Raw text data received from WebSocket.
        """
        try:
            message_data = self.parse_message(text_data)
            if not message_data:
                return

            message_type = message_data.get("type", "message")

            # Handle ping/pong for connection stability
            if message_type == "ping":
                await self.send_json(
                    {"type": "pong", "timestamp": datetime.now().isoformat()}
                )
                return

            # Route message to appropriate handler
            if message_type == "message":
                await self.handle_message(message_data)
            elif message_type == "typing":
                await self.handle_typing(message_data)
            elif message_type == "reaction":
                await self.handle_reaction(message_data)
            else:
                logger.warning(f"Unknown message type: {message_type}")

        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")
            await self.send_json(
                {"type": "error", "message": "Failed to process message"}
            )

    # Event handlers for group messages
    async def user_joined(self, event):
        """Broadcast user joined event to all connected clients."""
        logger.info(f"Broadcasting user_joined: {event['username']}")
        await self.send_json(
            {
                "type": "user_joined",
                "user_id": event["user_id"],
                "username": event["username"],
                "participants": event["participants"],
            }
        )

    async def user_left(self, event):
        """Broadcast user left event to all connected clients."""
        logger.info(f"Broadcasting user_left: {event['username']}")
        await self.send_json(
            {
                "type": "user_left",
                "user_id": event["user_id"],
                "username": event["username"],
                "participants": event["participants"],
            }
        )

    async def moderation_action(self, event):
        """
        Handle moderation action broadcasts.

        Broadcasts moderation actions (mute, warn, kick) to all participants.

        Args:
            event: Event data containing moderation action details.
        """
        logger.info(
            f"Broadcasting moderation action: {event['action']} "
            f"on {event['target_username']}"
        )
        await self.send_json(
            {
                "type": "moderation_action",
                "action": event["action"],
                "target_user_id": event["target_user_id"],
                "target_username": event["target_username"],
                "moderator": event["moderator"],
                "reason": event.get("reason", ""),
                "warnings_count": event.get("warnings_count", 0),
                "participants": event["participants"],
            }
        )

    async def participant_update(self, event):
        """
        Send participant list updates to connected clients.

        Args:
            event: Event data containing updated participant list.
        """
        await self.send_json(
            {
                "type": "participant_update",
                "participants": event.get("participants", []),
            }
        )

    async def session_status_update(self, event):
        """
        Handle session status updates.

        Broadcasts session phase changes (joining window, debate start,
        voting, completion) to all connected clients.

        Args:
            event: Event data containing session status information.
        """
        logger.info(f"Broadcasting session status update: {event['event_type']}")
        await self.send_json(
            {
                "type": "session_status_update",
                "event_type": event["event_type"],
                "session_status": event["session_status"],
                "timestamp": event["timestamp"],
                "joining_window_end": event.get("joining_window_end"),
                "debate_end_time": event.get("debate_end_time"),
                "voting_end_time": event.get("voting_end_time"),
                "winner": event.get("winner"),
                "total_votes": event.get("total_votes"),
                "reason": event.get("reason"),  # For cancellation
            }
        )

    @database_sync_to_async
    def get_debate_session(self, debate_id):
        """
        Retrieve debate session from database.

        Args:
            debate_id: ID of the debate session to retrieve.

        Returns:
            DebateSession: The debate session instance or None if not found.
        """
        from ..models import DebateSession

        try:
            logger.info(f"Looking up debate session: {debate_id}")
            session = DebateSession.objects.get(id=debate_id)
            logger.info(f"Debate session found: {session.topic}")
            return session
        except DebateSession.DoesNotExist:
            logger.error(f"Debate session {debate_id} does not exist")
            return None
        except Exception as e:
            logger.error(f"Unexpected error looking up debate session: {e}")
            return None

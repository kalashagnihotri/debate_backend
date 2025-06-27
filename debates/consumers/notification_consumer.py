"""
WebSocket consumer for personal user notifications.
"""

import json
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .base import BaseConsumerMixin

logger = logging.getLogger(__name__)


class NotificationConsumer(BaseConsumerMixin, AsyncWebsocketConsumer):
    """Consumer for personal user notifications"""

    async def connect(self):
        # Authenticate user
        user = await self.authenticate_connection()
        if not user:
            return

        self.user = user
        self.user_group = f"notifications_{user.id}"

        # Join user's personal notification group
        await self.channel_layer.group_add(
            self.user_group,
            self.channel_name
        )

        await self.accept()

        # Send current unread notification count
        unread_count = await self.get_unread_count()
        await self.send_json({
            'type': 'unread_count',
            'count': unread_count
        })

    async def disconnect(self, close_code):
        if hasattr(self, 'user_group'):
            await self.channel_layer.group_discard(
                self.user_group,
                self.channel_name
            )

    async def receive(self, text_data):
        # Handle incoming messages (like marking notifications as read)
        message_data = self.parse_message(text_data)
        if not message_data:
            return

        message_type = message_data.get('type')

        if message_type == 'mark_read':
            notification_ids = message_data.get('notification_ids', [])
            await self.mark_notifications_read(notification_ids)

            # Send updated unread count
            unread_count = await self.get_unread_count()
            await self.send_json({
                'type': 'unread_count',
                'count': unread_count
            })

    async def notification_received(self, event):
        """Handle new notification received"""
        await self.send_json({
            'type': 'new_notification',
            'notification': event['notification']
        })

        # Send updated unread count
        unread_count = await self.get_unread_count()
        await self.send_json({
            'type': 'unread_count',
            'count': unread_count
        })

    @database_sync_to_async
    def get_unread_count(self):
        from ..services.notification_service import notification_service
        return notification_service.get_unread_count(self.user)

    @database_sync_to_async
    def mark_notifications_read(self, notification_ids):
        from ..services.notification_service import notification_service
        return notification_service.mark_notifications_as_read(
            self.user,
            notification_ids if notification_ids else None
        )

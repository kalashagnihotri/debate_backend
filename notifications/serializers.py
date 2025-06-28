"""
Serializers for the notifications app.

Provides serialization for notification models including
proper formatting and validation.
"""

from rest_framework import serializers
from users.serializers import UserSerializer

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for notification model.

    Provides formatted notification data for API responses.
    """

    user = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "user", "message", "type", "is_read", "created_at"]
        read_only_fields = ["id", "created_at"]

    def to_representation(self, instance):
        """Customize the serialized representation"""
        data = super().to_representation(instance)

        # Format the created_at field
        if instance.created_at:
            data["created_at"] = instance.created_at.isoformat()

        # Add type display name
        data["type_display"] = instance.get_type_display()

        return data


class NotificationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating notifications.

    Used by the notification service to create new notifications.
    """

    class Meta:
        model = Notification
        fields = ["user", "message", "type"]

    def create(self, validated_data):
        """Create a new notification"""
        return Notification.objects.create(**validated_data)

"""
Serializers for user authentication and profile management.

This module contains Django REST framework serializers for user registration,
authentication, and profile data serialization.
"""

from rest_framework import serializers

from .models import Profile, User


class UserSerializer(serializers.ModelSerializer):
    """
    Basic user serializer for public user information.

    Used for displaying user data in lists and references.
    """

    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for new user registration.

    Handles user creation with proper password hashing and validation.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="Password must be at least 8 characters long",
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "role"]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        """
        Create a new user with hashed password.

        Args:
            validated_data: Validated user data from request

        Returns:
            User: Newly created user instance
        """
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login validation."""

    email = serializers.EmailField()
    password = serializers.CharField()


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profiles with statistics.

    Includes read-only computed fields for user activity metrics.
    """

    # Include user statistics as read-only fields
    total_debates_participated = serializers.ReadOnlyField(
        source="user.total_debates_participated"
    )
    total_debates_won = serializers.ReadOnlyField(source="user.total_debates_won")
    total_messages_sent = serializers.ReadOnlyField(source="user.total_messages_sent")
    username = serializers.ReadOnlyField(source="user.username")
    email = serializers.ReadOnlyField(source="user.email")
    role = serializers.ReadOnlyField(source="user.role")

    class Meta:
        model = Profile
        fields = [
            "id",
            "username",
            "email",
            "role",
            "bio",
            "profile_picture",
            "date_joined",
            "last_active",
            "total_debates_participated",
            "total_debates_won",
            "total_messages_sent",
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Detailed user serializer with profile and statistics.

    Provides comprehensive user information including profile data
    and computed activity statistics.
    """

    profile = ProfileSerializer(read_only=True)
    total_debates_participated = serializers.ReadOnlyField()
    total_debates_won = serializers.ReadOnlyField()
    total_messages_sent = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "date_joined",
            "total_debates_participated",
            "total_debates_won",
            "total_messages_sent",
            "profile",
        ]

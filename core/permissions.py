"""
Core permission classes for the debate platform.

This module defines custom permission classes that control access to various
parts of the debate platform based on user roles and participation status.
"""

from debates.models import Participation
from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    """
    Permission that allows access only to users with moderator role.

    This permission checks if the requesting user is authenticated and
    has the 'moderator' role assigned to their user account.
    """

    def has_permission(self, request, view):
        """
        Check if the user has moderator permissions.

        Args:
            request: The HTTP request object
            view: The view being accessed

        Returns:
            bool: True if user is authenticated and has moderator role
        """
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "moderator"
        )


class IsSessionModerator(BasePermission):
    """
    Permission that allows access only to the moderator of a specific session.

    This permission checks if the requesting user is the designated moderator
    for the specific debate session object being accessed.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if the user is the moderator of the specific session.

        Args:
            request: The HTTP request object
            view: The view being accessed
            obj: The session object being accessed

        Returns:
            bool: True if user is the session's moderator
        """
        return obj.moderator == request.user


class CanPostMessage(BasePermission):
    """
    Permission that allows users to post messages only if they are active participants.

    This permission checks if the user is a participant in the session and
    is not currently muted by a moderator.
    """

    def has_permission(self, request, view):
        """
        Check if the user can post messages in the session.

        Args:
            request: The HTTP request object
            view: The view being accessed

        Returns:
            bool: True if user is an active (non-muted) participant
        """
        session_pk = request.query_params.get("session_pk")
        if not session_pk:
            return False

        try:
            participation = Participation.objects.get(
                session_id=session_pk, user=request.user
            )
            # User must be a participant and not muted
            return participation.role == "participant" and not participation.is_muted
        except Participation.DoesNotExist:
            return False


class CanViewMessages(BasePermission):
    """
    Permission that allows users to view messages if they are session participants.

    This permission checks if the user is a participant in the session.
    Muted participants can still view messages but cannot post them.
    """

    def has_permission(self, request, view):
        """
        Check if the user can view messages in the session.

        Args:
            request: The HTTP request object
            view: The view being accessed

        Returns:
            bool: True if user is a participant (muted or active)
        """
        session_pk = request.query_params.get("session_pk")
        if not session_pk:
            return False

        try:
            participation = Participation.objects.get(
                session_id=session_pk, user=request.user
            )
            # User must be a participant (can be muted but still see messages)
            return participation.role == "participant"
        except Participation.DoesNotExist:
            return False

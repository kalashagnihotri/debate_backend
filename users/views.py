"""
User views for the debate platform.

This module contains API views for user registration, authentication,
profile management, and user statistics.
"""

from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Profile, User
from .serializers import (
    ProfileSerializer,
    UserDetailSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)


class UserRegistrationView(generics.CreateAPIView):
    """
    API view for user registration.

    Allows anonymous users to create new accounts with proper validation.
    """

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class UserListView(generics.ListAPIView):
    """
    API view for listing all users.

    Requires authentication and could be restricted to admin users only.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]  # Could be IsAdminUser for more security


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting specific users.

    Provides full CRUD operations for individual user records.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class CurrentUserProfileView(generics.RetrieveAPIView):
    """
    Get current user's profile information.

    Returns:
        Response: Serialized user data for the authenticated user
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Return the current authenticated user."""
        return self.request.user


class ProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user profiles with comprehensive statistics.

    Provides CRUD operations for user profiles including
    debate statistics and activity tracking.
    """

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return profiles filtered by current user."""
        if hasattr(self.request, "user") and self.request.user.is_authenticated:
            return Profile.objects.filter(user=self.request.user)
        return Profile.objects.none()

    @action(detail=False, methods=["get"])
    def me(self, request):
        """
        Get current user's profile with statistics.

        Creates profile if it doesn't exist for the user.

        Returns:
            Response: Serialized profile data with statistics
        """
        profile, created = Profile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=["patch", "put"])
    def update_profile(self, request):
        """
        Update current user's profile.

        Supports both partial (PATCH) and full (PUT) updates.

        Returns:
            Response: Updated profile data or validation errors
        """
        profile, created = Profile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserStatsView(generics.RetrieveAPIView):
    """
    API view for retrieving user statistics.

    Returns comprehensive statistics for the authenticated user
    including debate participation and performance metrics.
    """

    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Return the current authenticated user."""
        return self.request.user


class CurrentUserDetailView(generics.RetrieveAPIView):
    """
    Get current user's detailed profile with statistics.

    Returns:
        Response: Detailed user profile data with participation statistics
    """

    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Return the current authenticated user."""
        return self.request.user

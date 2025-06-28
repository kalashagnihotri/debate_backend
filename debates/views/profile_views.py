"""
User profile-related views for the debates app.
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..models import UserProfile
from ..serializers import UserProfileSerializer


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user profiles"""

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.all()

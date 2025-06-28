"""
URL configuration for users app.

Defines URL patterns for user authentication, registration,
profile management, and user-related API endpoints.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .auth_views import auth_status
from .views import (
    CurrentUserProfileView,
    ProfileViewSet,
    UserDetailView,
    UserListView,
    UserRegistrationView,
    UserStatsView,
)

# Router for ViewSet-based endpoints
router = DefaultRouter()
router.register(r"profiles", ProfileViewSet, basename="profile")

urlpatterns = [
    # User authentication and registration
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("auth-status/", auth_status, name="auth-status"),
    # User profile endpoints
    path("profile/", CurrentUserProfileView.as_view(), name="user-profile"),
    path("me/", CurrentUserProfileView.as_view(), name="current-user-profile"),
    path("stats/", UserStatsView.as_view(), name="user-stats"),
    # User CRUD endpoints
    path("", UserListView.as_view(), name="user-list"),
    path("<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    # Router-based endpoints
    path("", include(router.urls)),
]

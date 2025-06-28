"""
Tests for users app.

This module contains comprehensive tests for user authentication,
registration, profile management, and user-related API endpoints.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile

User = get_user_model()


class UserRegistrationTestCase(APITestCase):
    """Test user registration functionality."""

    def setUp(self):
        """Set up test data."""
        self.registration_url = reverse("register")
        self.valid_user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "role": "student",
        }

    def test_user_registration_success(self):
        """Test successful user registration."""
        response = self.client.post(self.registration_url, self.valid_user_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="testuser").exists())

        user = User.objects.get(username="testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.role, "student")

    def test_user_registration_duplicate_username(self):
        """Test registration with duplicate username."""
        # Create first user
        User.objects.create_user(
            username="testuser", email="first@example.com", password="testpass123"
        )

        response = self.client.post(self.registration_url, self.valid_user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_user_registration_invalid_email(self):
        """Test registration with invalid email."""
        invalid_data = self.valid_user_data.copy()
        invalid_data["email"] = "invalid-email"

        response = self.client.post(self.registration_url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_user_registration_missing_fields(self):
        """Test registration with missing required fields."""
        incomplete_data = {"username": "testuser"}

        response = self.client.post(self.registration_url, incomplete_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertIn("password", response.data)

    def test_user_registration_invalid_role(self):
        """Test registration with invalid role."""
        invalid_data = self.valid_user_data.copy()
        invalid_data["role"] = "invalid_role"

        response = self.client.post(self.registration_url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserAuthenticationTestCase(APITestCase):
    """Test user authentication functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role="student",
        )
        self.token_url = reverse("token_obtain_pair")
        self.auth_status_url = reverse("auth-status")

    def test_token_obtain_success(self):
        """Test successful token obtainment."""
        login_data = {"username": "testuser", "password": "testpass123"}

        response = self.client.post(self.token_url, login_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_token_obtain_invalid_credentials(self):
        """Test token obtainment with invalid credentials."""
        login_data = {"username": "testuser", "password": "wrongpassword"}

        response = self.client.post(self.token_url, login_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_status_authenticated(self):
        """Test auth status for authenticated user."""
        # Get token and authenticate
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = self.client.get(self.auth_status_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_authenticated"])
        self.assertEqual(response.data["user"]["username"], "testuser")

    def test_auth_status_unauthenticated(self):
        """Test auth status for unauthenticated user."""
        response = self.client.get(self.auth_status_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_authenticated"])
        self.assertIsNone(response.data["user"])


class UserProfileTestCase(APITestCase):
    """Test user profile functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role="student",
        )
        self.moderator = User.objects.create_user(
            username="moderator",
            email="moderator@example.com",
            password="testpass123",
            role="moderator",
        )

        # Create JWT tokens
        self.user_token = RefreshToken.for_user(self.user).access_token
        self.moderator_token = RefreshToken.for_user(self.moderator).access_token

        self.profile_url = reverse("current-user-profile")
        self.user_stats_url = reverse("user-stats")

    def test_get_current_user_profile(self):
        """Test retrieving current user profile."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["role"], "student")

    def test_get_current_user_profile_unauthenticated(self):
        """Test retrieving profile without authentication."""
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_stats(self):
        """Test retrieving user statistics."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        response = self.client.get(self.user_stats_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_debates_participated", response.data)
        self.assertIn("debates_won", response.data)

    def test_profile_viewset_me_endpoint(self):
        """Test profile viewset me endpoint."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        url = reverse("profile-me")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Profile should be created automatically if it doesn't exist
        self.assertTrue(Profile.objects.filter(user=self.user).exists())


class UserListViewTestCase(APITestCase):
    """Test user list and detail views."""

    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="testpass123",
            role="student",
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="testpass123",
            role="moderator",
        )

        self.token = RefreshToken.for_user(self.user1).access_token
        self.user_list_url = reverse("user-list")

    def test_get_user_list_authenticated(self):
        """Test retrieving user list when authenticated."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.get(self.user_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_get_user_list_unauthenticated(self):
        """Test retrieving user list without authentication."""
        response = self.client.get(self.user_list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_detail(self):
        """Test retrieving specific user details."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        url = reverse("user-detail", kwargs={"pk": self.user2.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "user2")
        self.assertEqual(response.data["role"], "moderator")


class UserModelTestCase(APITestCase):
    """Test User model functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role="student",
        )

    def test_user_string_representation(self):
        """Test user string representation."""
        self.assertEqual(str(self.user), "testuser")

    def test_user_role_choices(self):
        """Test user role choices."""
        # Test valid roles
        self.user.role = "student"
        self.user.save()
        self.assertEqual(self.user.role, "student")

        self.user.role = "moderator"
        self.user.save()
        self.assertEqual(self.user.role, "moderator")

    def test_user_default_role(self):
        """Test user default role."""
        new_user = User.objects.create_user(
            username="newuser", email="new@example.com", password="testpass123"
        )
        self.assertEqual(new_user.role, "student")

    def test_total_debates_participated_property(self):
        """Test total_debates_participated property."""
        # Should return 0 when no participations exist
        self.assertEqual(self.user.total_debates_participated, 0)

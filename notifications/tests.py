"""
Tests for notifications app.

This module contains comprehensive tests for notification functionality
including creation, retrieval, and marking as read.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Notification

User = get_user_model()


class NotificationTestCase(APITestCase):
    """Test notification functionality."""

    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123',
            role='student'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123',
            role='student'
        )
        
        self.user1_token = RefreshToken.for_user(self.user1).access_token
        self.user2_token = RefreshToken.for_user(self.user2).access_token
        
        self.notifications_url = reverse('get-notifications')
        self.mark_read_url = reverse('mark-notifications-read')
        self.stats_url = reverse('notification-stats')

    def test_get_notifications_authenticated(self):
        """Test retrieving notifications for authenticated user."""
        # Create notifications for user1
        Notification.objects.create(
            user=self.user1,
            title='Test Notification 1',
            message='Test message 1',
            notification_type='debate_invitation'
        )
        Notification.objects.create(
            user=self.user1,
            title='Test Notification 2',
            message='Test message 2',
            notification_type='debate_started'
        )
        # Create notification for user2 (should not appear for user1)
        Notification.objects.create(
            user=self.user2,
            title='User2 Notification',
            message='Should not appear for user1',
            notification_type='debate_ended'
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        
        response = self.client.get(self.notifications_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        # Check that only user1's notifications are returned
        titles = [notif['title'] for notif in response.data['results']]
        self.assertIn('Test Notification 1', titles)
        self.assertIn('Test Notification 2', titles)
        self.assertNotIn('User2 Notification', titles)

    def test_get_notifications_unauthenticated(self):
        """Test retrieving notifications without authentication."""
        response = self.client.get(self.notifications_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_notifications_empty(self):
        """Test retrieving notifications when user has none."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        
        response = self.client.get(self.notifications_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_get_notifications_filtering(self):
        """Test filtering notifications by read status."""
        # Create read and unread notifications
        read_notif = Notification.objects.create(
            user=self.user1,
            title='Read Notification',
            message='This is read',
            notification_type='debate_started',
            is_read=True
        )
        unread_notif = Notification.objects.create(
            user=self.user1,
            title='Unread Notification',
            message='This is unread',
            notification_type='debate_ended',
            is_read=False
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        
        # Test getting only unread notifications
        response = self.client.get(f'{self.notifications_url}?is_read=false')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Unread Notification')

    def test_mark_notifications_as_read(self):
        """Test marking notifications as read."""
        # Create unread notifications
        notif1 = Notification.objects.create(
            user=self.user1,
            title='Notification 1',
            message='Message 1',
            notification_type='debate_started',
            is_read=False
        )
        notif2 = Notification.objects.create(
            user=self.user1,
            title='Notification 2',
            message='Message 2',
            notification_type='debate_ended',
            is_read=False
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        
        mark_read_data = {
            'notification_ids': [notif1.pk, notif2.pk]
        }
        
        response = self.client.post(self.mark_read_url, mark_read_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that notifications are marked as read
        notif1.refresh_from_db()
        notif2.refresh_from_db()
        self.assertTrue(notif1.is_read)
        self.assertTrue(notif2.is_read)
        self.assertIsNotNone(notif1.read_at)
        self.assertIsNotNone(notif2.read_at)

    def test_mark_notifications_as_read_invalid_ids(self):
        """Test marking notifications as read with invalid IDs."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        
        mark_read_data = {
            'notification_ids': [9999, 9998]  # Non-existent IDs
        }
        
        response = self.client.post(self.mark_read_url, mark_read_data, format='json')
        
        # Should still return 200 but with appropriate message
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mark_notifications_as_read_other_user_notifications(self):
        """Test that user cannot mark other user's notifications as read."""
        # Create notification for user2
        notif = Notification.objects.create(
            user=self.user2,
            title='User2 Notification',
            message='Message for user2',
            notification_type='debate_started',
            is_read=False
        )
        
        # Try to mark it as read using user1's token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        
        mark_read_data = {
            'notification_ids': [notif.pk]
        }
        
        response = self.client.post(self.mark_read_url, mark_read_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Notification should remain unread since user1 can't modify user2's notifications
        notif.refresh_from_db()
        self.assertFalse(notif.is_read)

    def test_mark_all_notifications_as_read(self):
        """Test marking all notifications as read."""
        # Create several unread notifications
        Notification.objects.create(
            user=self.user1,
            title='Notification 1',
            message='Message 1',
            notification_type='debate_started',
            is_read=False
        )
        Notification.objects.create(
            user=self.user1,
            title='Notification 2',
            message='Message 2',
            notification_type='debate_ended',
            is_read=False
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        
        # Send empty list or special indicator to mark all as read
        mark_read_data = {
            'mark_all': True
        }
        
        response = self.client.post(self.mark_read_url, mark_read_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that all user1's notifications are marked as read
        user1_notifications = Notification.objects.filter(user=self.user1)
        for notif in user1_notifications:
            self.assertTrue(notif.is_read)

    def test_get_notification_stats(self):
        """Test retrieving notification statistics."""
        # Create various notifications
        Notification.objects.create(
            user=self.user1,
            title='Read Notification',
            message='Message',
            notification_type='debate_started',
            is_read=True
        )
        Notification.objects.create(
            user=self.user1,
            title='Unread Notification 1',
            message='Message',
            notification_type='debate_ended',
            is_read=False
        )
        Notification.objects.create(
            user=self.user1,
            title='Unread Notification 2',
            message='Message',
            notification_type='debate_invitation',
            is_read=False
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        
        response = self.client.get(self.stats_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_notifications'], 3)
        self.assertEqual(response.data['unread_notifications'], 2)
        self.assertEqual(response.data['read_notifications'], 1)

    def test_get_notification_stats_unauthenticated(self):
        """Test retrieving notification stats without authentication."""
        response = self.client.get(self.stats_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_notification_ordering(self):
        """Test that notifications are ordered by creation date (newest first)."""
        # Create notifications at different times
        old_notif = Notification.objects.create(
            user=self.user1,
            title='Old Notification',
            message='Old message',
            notification_type='debate_started'
        )
        old_notif.created_at = timezone.now() - timezone.timedelta(hours=2)
        old_notif.save()
        
        new_notif = Notification.objects.create(
            user=self.user1,
            title='New Notification',
            message='New message',
            notification_type='debate_ended'
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        
        response = self.client.get(self.notifications_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Newest should be first
        self.assertEqual(response.data['results'][0]['title'], 'New Notification')
        self.assertEqual(response.data['results'][1]['title'], 'Old Notification')

    def test_notification_pagination(self):
        """Test notification pagination."""
        # Create many notifications
        for i in range(25):
            Notification.objects.create(
                user=self.user1,
                title=f'Notification {i}',
                message=f'Message {i}',
                notification_type='debate_started'
            )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        
        response = self.client.get(self.notifications_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertEqual(response.data['count'], 25)
        
        # Test pagination
        if response.data['next']:
            next_response = self.client.get(response.data['next'])
            self.assertEqual(next_response.status_code, status.HTTP_200_OK)


class NotificationModelTestCase(APITestCase):
    """Test Notification model functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='student'
        )

    def test_notification_creation(self):
        """Test notification creation."""
        notification = Notification.objects.create(
            user=self.user,
            title='Test Notification',
            message='Test message',
            notification_type='debate_started'
        )
        
        self.assertEqual(str(notification), 'Test Notification')
        self.assertFalse(notification.is_read)
        self.assertIsNone(notification.read_at)
        self.assertIsNotNone(notification.created_at)

    def test_notification_string_representation(self):
        """Test notification string representation."""
        notification = Notification.objects.create(
            user=self.user,
            title='Test Title',
            message='Test message',
            notification_type='debate_ended'
        )
        
        self.assertEqual(str(notification), 'Test Title')

    def test_notification_type_choices(self):
        """Test notification type choices."""
        valid_types = [
            'debate_invitation',
            'debate_started',
            'debate_ended',
            'moderation_action',
            'session_update'
        ]
        
        for notif_type in valid_types:
            notification = Notification.objects.create(
                user=self.user,
                title=f'Test {notif_type}',
                message='Test message',
                notification_type=notif_type
            )
            self.assertEqual(notification.notification_type, notif_type)

    def test_mark_as_read(self):
        """Test marking notification as read."""
        notification = Notification.objects.create(
            user=self.user,
            title='Test Notification',
            message='Test message',
            notification_type='debate_started',
            is_read=False
        )
        
        # Simulate marking as read
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        self.assertTrue(notification.is_read)
        self.assertIsNotNone(notification.read_at)

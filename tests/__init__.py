"""
Integration tests for the Online Debate Platform.

This module contains integration tests that test the complete workflow
of the debate platform including authentication, session lifecycle,
and end-to-end user interactions.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from debates.models import DebateTopic, DebateSession, Message, Participation, Vote
from notifications.models import Notification

User = get_user_model()


class DebateWorkflowIntegrationTestCase(APITestCase):
    """Test complete debate workflow from start to finish."""

    def setUp(self):
        """Set up test data for integration tests."""
        # Create users
        self.moderator = User.objects.create_user(
            username='moderator',
            email='moderator@example.com',
            password='testpass123',
            role='moderator'
        )
        self.student1 = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='testpass123',
            role='student'
        )
        self.student2 = User.objects.create_user(
            username='student2',
            email='student2@example.com',
            password='testpass123',
            role='student'
        )
        self.viewer = User.objects.create_user(
            username='viewer',
            email='viewer@example.com',
            password='testpass123',
            role='student'
        )
        
        # Create tokens
        self.moderator_token = RefreshToken.for_user(self.moderator).access_token
        self.student1_token = RefreshToken.for_user(self.student1).access_token
        self.student2_token = RefreshToken.for_user(self.student2).access_token
        self.viewer_token = RefreshToken.for_user(self.viewer).access_token

    def test_complete_debate_workflow(self):
        """Test the complete debate workflow from topic creation to voting."""
        
        # Step 1: Moderator creates a topic
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.moderator_token}')
        
        topic_data = {
            'title': 'Should artificial intelligence be regulated?',
            'description': 'A debate about AI regulation and its implications',
            'category': 'Technology'
        }
        
        topics_url = reverse('topic-list')
        response = self.client.post(topics_url, topic_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        topic_id = response.data['id']
        
        # Step 2: Moderator creates a debate session
        session_data = {
            'topic': topic_id,
            'scheduled_start': (timezone.now() + timezone.timedelta(minutes=30)).isoformat(),
            'duration_minutes': 60
        }
        
        sessions_url = reverse('session-list')
        response = self.client.post(sessions_url, session_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        session_id = response.data['id']
        
        # Step 3: Moderator starts the joining phase
        start_joining_url = reverse('session-start-joining', kwargs={'pk': session_id})
        response = self.client.post(start_joining_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 4: Students join as participants
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student1_token}')
        
        join_url = reverse('session-join', kwargs={'pk': session_id})
        join_data = {
            'role': 'participant',
            'side': 'proposition'
        }
        response = self.client.post(join_url, join_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Student 2 joins opposition
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student2_token}')
        
        join_data = {
            'role': 'participant',
            'side': 'opposition'
        }
        response = self.client.post(join_url, join_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Viewer joins as viewer
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.viewer_token}')
        
        join_data = {'role': 'viewer'}
        response = self.client.post(join_url, join_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 5: Moderator starts the debate
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.moderator_token}')
        
        start_debate_url = reverse('session-start-debate', kwargs={'pk': session_id})
        response = self.client.post(start_debate_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 6: Participants send messages
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student1_token}')
        
        messages_url = reverse('message-list')
        message_data = {
            'session': session_id,
            'content': 'AI regulation is necessary to prevent potential misuse and ensure ethical development.',
            'message_type': 'argument'
        }
        response = self.client.post(messages_url, message_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Student 2 responds
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student2_token}')
        
        message_data = {
            'session': session_id,
            'content': 'Over-regulation could stifle innovation and prevent beneficial AI development.',
            'message_type': 'argument'
        }
        response = self.client.post(messages_url, message_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Step 7: Moderator starts voting phase
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.moderator_token}')
        
        start_voting_url = reverse('session-start-voting', kwargs={'pk': session_id})
        response = self.client.post(start_voting_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 8: Viewer votes
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.viewer_token}')
        
        vote_url = reverse('submit-vote', kwargs={'session_id': session_id})
        vote_data = {'vote_type': 'proposition'}
        response = self.client.post(vote_url, vote_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Step 9: Get voting results
        results_url = reverse('voting-results', kwargs={'session_id': session_id})
        response = self.client.get(results_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['proposition_votes'], 1)
        self.assertEqual(response.data['opposition_votes'], 0)
        
        # Step 10: Moderator ends the session
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.moderator_token}')
        
        end_session_url = reverse('session-end-session', kwargs={'pk': session_id})
        response = self.client.post(end_session_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 11: Verify session transcript is available
        transcript_url = reverse('session-transcript', kwargs={'pk': session_id})
        response = self.client.get(transcript_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('messages', response.data)
        self.assertEqual(len(response.data['messages']), 2)

    def test_moderation_workflow(self):
        """Test moderation actions during a debate."""
        
        # Setup: Create topic and session
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.moderator_token}')
        
        topic = DebateTopic.objects.create(
            title='Test Topic',
            description='Test Description',
            category='Test',
            created_by=self.moderator
        )
        
        session = DebateSession.objects.create(
            topic=topic,
            moderator=self.moderator,
            scheduled_start=timezone.now() + timezone.timedelta(minutes=30),
            duration_minutes=60,
            status='online'
        )
        
        # Student joins as participant
        Participation.objects.create(
            session=session,
            user=self.student1,
            role='participant',
            side='proposition'
        )
        
        # Step 1: Student sends a message
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student1_token}')
        
        messages_url = reverse('message-list')
        message_data = {
            'session': session.pk,
            'content': 'This is an inappropriate message',
            'message_type': 'argument'
        }
        response = self.client.post(messages_url, message_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Step 2: Moderator warns the participant
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.moderator_token}')
        
        warn_url = reverse('session-warn-participant', kwargs={'pk': session.pk})
        warn_data = {
            'user_id': self.student1.pk,
            'reason': 'Inappropriate language'
        }
        response = self.client.post(warn_url, warn_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 3: Moderator mutes the participant
        mute_url = reverse('session-mute-participant', kwargs={'pk': session.pk})
        mute_data = {
            'user_id': self.student1.pk,
            'reason': 'Continued inappropriate behavior'
        }
        response = self.client.post(mute_url, mute_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 4: Verify participant is muted
        participation = Participation.objects.get(session=session, user=self.student1)
        self.assertTrue(participation.is_muted)
        
        # Step 5: Muted participant tries to send message (should fail)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student1_token}')
        
        message_data = {
            'session': session.pk,
            'content': 'I should not be able to send this',
            'message_type': 'argument'
        }
        response = self.client.post(messages_url, message_data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authentication_flow(self):
        """Test complete authentication and authorization flow."""
        
        # Step 1: Register new user
        register_url = reverse('register')
        registration_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'role': 'student'
        }
        response = self.client.post(register_url, registration_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Step 2: Login to get token
        token_url = reverse('token_obtain_pair')
        login_data = {
            'username': 'newuser',
            'password': 'newpass123'
        }
        response = self.client.post(token_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data['access']
        refresh_token = response.data['refresh']
        
        # Step 3: Use token to access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        profile_url = reverse('current-user-profile')
        response = self.client.get(profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'newuser')
        
        # Step 4: Test token refresh
        refresh_url = reverse('token_refresh')
        refresh_data = {'refresh': refresh_token}
        response = self.client.post(refresh_url, refresh_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_access_token = response.data['access']
        
        # Step 5: Use new token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')
        
        response = self.client.get(profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'newuser')

    def test_permission_enforcement(self):
        """Test that permissions are properly enforced across the system."""
        
        # Create topic as moderator
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.moderator_token}')
        
        topic_data = {
            'title': 'Permission Test Topic',
            'description': 'Testing permissions',
            'category': 'Test'
        }
        
        topics_url = reverse('topic-list')
        response = self.client.post(topics_url, topic_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        topic_id = response.data['id']
        
        # Test 1: Student cannot create topics
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student1_token}')
        
        response = self.client.post(topics_url, topic_data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test 2: Student cannot create sessions
        session_data = {
            'topic': topic_id,
            'scheduled_start': (timezone.now() + timezone.timedelta(minutes=30)).isoformat(),
            'duration_minutes': 60
        }
        
        sessions_url = reverse('session-list')
        response = self.client.post(sessions_url, session_data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test 3: Create session as moderator
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.moderator_token}')
        
        response = self.client.post(sessions_url, session_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        session_id = response.data['id']
        
        # Test 4: Student cannot perform moderation actions
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student1_token}')
        
        mute_url = reverse('session-mute-participant', kwargs={'pk': session_id})
        mute_data = {
            'user_id': self.student2.pk,
            'reason': 'Student cannot do this'
        }
        response = self.client.post(mute_url, mute_data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_notification_system_integration(self):
        """Test notification system integration with debate events."""
        
        # Create a debate session
        topic = DebateTopic.objects.create(
            title='Notification Test Topic',
            description='Testing notifications',
            category='Test',
            created_by=self.moderator
        )
        
        session = DebateSession.objects.create(
            topic=topic,
            moderator=self.moderator,
            scheduled_start=timezone.now() + timezone.timedelta(minutes=30),
            duration_minutes=60,
            status='scheduled'
        )
        
        # Manually create a notification (in real app, this would be triggered by signals)
        Notification.objects.create(
            user=self.student1,
            title='New debate session created',
            message=f'A new debate session "{topic.title}" has been scheduled',
            notification_type='debate_invitation'
        )
        
        # Test 1: User can retrieve their notifications
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student1_token}')
        
        notifications_url = reverse('get-notifications')
        response = self.client.get(notifications_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'New debate session created')
        
        # Test 2: User can mark notification as read
        notification_id = response.data['results'][0]['id']
        
        mark_read_url = reverse('mark-notifications-read')
        mark_read_data = {
            'notification_ids': [notification_id]
        }
        response = self.client.post(mark_read_url, mark_read_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test 3: Verify notification is marked as read
        response = self.client.get(notifications_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['results'][0]['is_read'])

    def test_data_consistency_across_operations(self):
        """Test data consistency across multiple operations."""
        
        # Create complete debate setup
        topic = DebateTopic.objects.create(
            title='Consistency Test Topic',
            description='Testing data consistency',
            category='Test',
            created_by=self.moderator
        )
        
        session = DebateSession.objects.create(
            topic=topic,
            moderator=self.moderator,
            scheduled_start=timezone.now() + timezone.timedelta(minutes=30),
            duration_minutes=60,
            status='online'
        )
        
        # Add participants
        participation1 = Participation.objects.create(
            session=session,
            user=self.student1,
            role='participant',
            side='proposition'
        )
        
        participation2 = Participation.objects.create(
            session=session,
            user=self.student2,
            role='participant',
            side='opposition'
        )
        
        viewer_participation = Participation.objects.create(
            session=session,
            user=self.viewer,
            role='viewer'
        )
        
        # Test 1: Verify participant counts
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.moderator_token}')
        
        status_url = reverse('session-status', kwargs={'pk': session.pk})
        response = self.client.get(status_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['participant_count'], 2)
        self.assertEqual(response.data['viewer_count'], 1)
        
        # Test 2: Add messages and verify counts
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student1_token}')
        
        messages_url = reverse('message-list')
        message_data = {
            'session': session.pk,
            'content': 'First argument',
            'message_type': 'argument'
        }
        response = self.client.post(messages_url, message_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Test 3: Verify message appears in session messages
        response = self.client.get(f'{messages_url}?session_pk={session.pk}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['content'], 'First argument')
        
        # Test 4: User leaves session and verify counts update
        leave_url = reverse('session-leave', kwargs={'pk': session.pk})
        response = self.client.post(leave_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify counts are updated
        response = self.client.get(status_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['participant_count'], 1)  # One participant left

"""
Tests for debates app.

This module contains comprehensive tests for debate topics, sessions,
messages, voting, and moderation functionality.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import DebateTopic, DebateSession, Message, Participation, Vote

User = get_user_model()


class DebateTopicTestCase(APITestCase):
    """Test debate topic functionality."""

    def setUp(self):
        """Set up test data."""
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpass123',
            role='student'
        )
        self.moderator = User.objects.create_user(
            username='moderator',
            email='moderator@example.com',
            password='testpass123',
            role='moderator'
        )
        
        self.student_token = RefreshToken.for_user(self.student).access_token
        self.moderator_token = RefreshToken.for_user(self.moderator).access_token
        
        self.topics_url = reverse('topic-list')
        
        self.topic_data = {
            'title': 'Should AI replace human teachers?',
            'description': 'A debate about the role of AI in education',
            'category': 'Education'
        }

    def test_create_topic_as_moderator(self):
        """Test creating topic as moderator."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.moderator_token}')
        
        response = self.client.post(self.topics_url, self.topic_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(DebateTopic.objects.filter(title=self.topic_data['title']).exists())

    def test_create_topic_as_student_forbidden(self):
        """Test creating topic as student should be forbidden."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student_token}')
        
        response = self.client.post(self.topics_url, self.topic_data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_topic_unauthenticated(self):
        """Test creating topic without authentication."""
        response = self.client.post(self.topics_url, self.topic_data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_topics_public(self):
        """Test listing topics should be public."""
        # Create a topic
        topic = DebateTopic.objects.create(
            title='Test Topic',
            description='Test Description',
            category='Test',
            created_by=self.moderator
        )
        
        response = self.client.get(self.topics_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_topic_detail(self):
        """Test retrieving topic details."""
        topic = DebateTopic.objects.create(
            title='Test Topic',
            description='Test Description',
            category='Test',
            created_by=self.moderator
        )
        
        url = reverse('topic-detail', kwargs={'pk': topic.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Topic')

    def test_update_topic_as_moderator(self):
        """Test updating topic as moderator."""
        topic = DebateTopic.objects.create(
            title='Test Topic',
            description='Test Description',
            category='Test',
            created_by=self.moderator
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.moderator_token}')
        
        updated_data = {
            'title': 'Updated Topic',
            'description': 'Updated Description',
            'category': 'Updated'
        }
        
        url = reverse('topic-detail', kwargs={'pk': topic.pk})
        response = self.client.put(url, updated_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        topic.refresh_from_db()
        self.assertEqual(topic.title, 'Updated Topic')

    def test_delete_topic_as_moderator(self):
        """Test deleting topic as moderator."""
        topic = DebateTopic.objects.create(
            title='Test Topic',
            description='Test Description',
            category='Test',
            created_by=self.moderator
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.moderator_token}')
        
        url = reverse('topic-detail', kwargs={'pk': topic.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(DebateTopic.objects.filter(pk=topic.pk).exists())


class DebateSessionTestCase(APITestCase):
    """Test debate session functionality."""

    def setUp(self):
        """Set up test data."""
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpass123',
            role='student'
        )
        self.moderator = User.objects.create_user(
            username='moderator',
            email='moderator@example.com',
            password='testpass123',
            role='moderator'
        )
        
        self.student_token = RefreshToken.for_user(self.student).access_token
        self.moderator_token = RefreshToken.for_user(self.moderator).access_token
        
        self.topic = DebateTopic.objects.create(
            title='Test Topic',
            description='Test Description',
            category='Test',
            created_by=self.moderator
        )
        
        self.sessions_url = reverse('session-list')
        
        self.session_data = {
            'topic': self.topic.pk,
            'scheduled_start': (timezone.now() + timezone.timedelta(hours=1)).isoformat(),
            'duration_minutes': 60
        }

    def test_create_session_as_moderator(self):
        """Test creating session as moderator."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.moderator_token}')
        
        response = self.client.post(self.sessions_url, self.session_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(DebateSession.objects.filter(topic=self.topic).exists())

    def test_create_session_as_student_forbidden(self):
        """Test creating session as student should be forbidden."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student_token}')
        
        response = self.client.post(self.sessions_url, self.session_data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_sessions_public(self):
        """Test listing sessions should be public."""
        session = DebateSession.objects.create(
            topic=self.topic,
            moderator=self.moderator,
            scheduled_start=timezone.now() + timezone.timedelta(hours=1),
            duration_minutes=60
        )
        
        response = self.client.get(self.sessions_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_join_session_as_participant(self):
        """Test joining session as participant."""
        session = DebateSession.objects.create(
            topic=self.topic,
            moderator=self.moderator,
            scheduled_start=timezone.now() + timezone.timedelta(hours=1),
            duration_minutes=60,
            status='joining'
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student_token}')
        
        url = reverse('session-join', kwargs={'pk': session.pk})
        join_data = {
            'role': 'participant',
            'side': 'proposition'
        }
        
        response = self.client.post(url, join_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            Participation.objects.filter(
                session=session,
                user=self.student,
                role='participant'
            ).exists()
        )

    def test_join_session_as_viewer(self):
        """Test joining session as viewer."""
        session = DebateSession.objects.create(
            topic=self.topic,
            moderator=self.moderator,
            scheduled_start=timezone.now() + timezone.timedelta(hours=1),
            duration_minutes=60,
            status='online'
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student_token}')
        
        url = reverse('session-join', kwargs={'pk': session.pk})
        join_data = {'role': 'viewer'}
        
        response = self.client.post(url, join_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            Participation.objects.filter(
                session=session,
                user=self.student,
                role='viewer'
            ).exists()
        )

    def test_leave_session(self):
        """Test leaving session."""
        session = DebateSession.objects.create(
            topic=self.topic,
            moderator=self.moderator,
            scheduled_start=timezone.now() + timezone.timedelta(hours=1),
            duration_minutes=60,
            status='online'
        )
        
        # First join the session
        Participation.objects.create(
            session=session,
            user=self.student,
            role='viewer'
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student_token}')
        
        url = reverse('session-leave', kwargs={'pk': session.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Participation should be marked as left, not deleted
        participation = Participation.objects.get(session=session, user=self.student)
        self.assertIsNotNone(participation.left_at)

    def test_get_session_status(self):
        """Test getting session status."""
        session = DebateSession.objects.create(
            topic=self.topic,
            moderator=self.moderator,
            scheduled_start=timezone.now() + timezone.timedelta(hours=1),
            duration_minutes=60,
            status='online'
        )
        
        url = reverse('session-status', kwargs={'pk': session.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('phase', response.data)
        self.assertIn('participant_count', response.data)
        self.assertIn('viewer_count', response.data)


class MessageTestCase(APITestCase):
    """Test message functionality."""

    def setUp(self):
        """Set up test data."""
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpass123',
            role='student'
        )
        self.moderator = User.objects.create_user(
            username='moderator',
            email='moderator@example.com',
            password='testpass123',
            role='moderator'
        )
        
        self.student_token = RefreshToken.for_user(self.student).access_token
        self.moderator_token = RefreshToken.for_user(self.moderator).access_token
        
        self.topic = DebateTopic.objects.create(
            title='Test Topic',
            description='Test Description',
            category='Test',
            created_by=self.moderator
        )
        
        self.session = DebateSession.objects.create(
            topic=self.topic,
            moderator=self.moderator,
            scheduled_start=timezone.now() + timezone.timedelta(hours=1),
            duration_minutes=60,
            status='online'
        )
        
        # Add student as participant
        Participation.objects.create(
            session=self.session,
            user=self.student,
            role='participant',
            side='proposition'
        )
        
        self.messages_url = reverse('message-list')

    def test_send_message_as_participant(self):
        """Test sending message as participant."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student_token}')
        
        message_data = {
            'session': self.session.pk,
            'content': 'This is my argument for the proposition.',
            'message_type': 'argument'
        }
        
        response = self.client.post(self.messages_url, message_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Message.objects.filter(
                session=self.session,
                author=self.student,
                content=message_data['content']
            ).exists()
        )

    def test_send_message_as_non_participant_forbidden(self):
        """Test sending message as non-participant should be forbidden."""
        non_participant = User.objects.create_user(
            username='outsider',
            email='outsider@example.com',
            password='testpass123',
            role='student'
        )
        
        token = RefreshToken.for_user(non_participant).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        message_data = {
            'session': self.session.pk,
            'content': 'I should not be able to send this.',
            'message_type': 'argument'
        }
        
        response = self.client.post(self.messages_url, message_data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_session_messages(self):
        """Test retrieving session messages."""
        # Create some messages
        Message.objects.create(
            session=self.session,
            author=self.student,
            content='Test message 1',
            message_type='argument'
        )
        Message.objects.create(
            session=self.session,
            author=self.moderator,
            content='Test message 2',
            message_type='question'
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student_token}')
        
        response = self.client.get(f'{self.messages_url}?session_pk={self.session.pk}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)


class VotingTestCase(APITestCase):
    """Test voting functionality."""

    def setUp(self):
        """Set up test data."""
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpass123',
            role='student'
        )
        self.viewer = User.objects.create_user(
            username='viewer',
            email='viewer@example.com',
            password='testpass123',
            role='student'
        )
        self.moderator = User.objects.create_user(
            username='moderator',
            email='moderator@example.com',
            password='testpass123',
            role='moderator'
        )
        
        self.student_token = RefreshToken.for_user(self.student).access_token
        self.viewer_token = RefreshToken.for_user(self.viewer).access_token
        self.moderator_token = RefreshToken.for_user(self.moderator).access_token
        
        self.topic = DebateTopic.objects.create(
            title='Test Topic',
            description='Test Description',
            category='Test',
            created_by=self.moderator
        )
        
        self.session = DebateSession.objects.create(
            topic=self.topic,
            moderator=self.moderator,
            scheduled_start=timezone.now() + timezone.timedelta(hours=1),
            duration_minutes=60,
            status='voting'
        )
        
        # Add users to session
        Participation.objects.create(
            session=self.session,
            user=self.student,
            role='participant',
            side='proposition'
        )
        Participation.objects.create(
            session=self.session,
            user=self.viewer,
            role='viewer'
        )

    def test_submit_vote_as_viewer(self):
        """Test submitting vote as viewer."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.viewer_token}')
        
        vote_url = reverse('submit-vote', kwargs={'session_id': self.session.pk})
        vote_data = {'vote_type': 'proposition'}
        
        response = self.client.post(vote_url, vote_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Vote.objects.filter(
                debate_session=self.session,
                user=self.viewer,
                vote_type='proposition'
            ).exists()
        )

    def test_submit_vote_as_participant_forbidden(self):
        """Test submitting vote as participant should be forbidden."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student_token}')
        
        vote_url = reverse('submit-vote', kwargs={'session_id': self.session.pk})
        vote_data = {'vote_type': 'proposition'}
        
        response = self.client.post(vote_url, vote_data)
        
        # Participants should not be able to vote
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_submit_duplicate_vote(self):
        """Test submitting duplicate vote should update previous vote."""
        # First vote
        Vote.objects.create(
            debate_session=self.session,
            user=self.viewer,
            vote_type='proposition'
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.viewer_token}')
        
        vote_url = reverse('submit-vote', kwargs={'session_id': self.session.pk})
        vote_data = {'vote_type': 'opposition'}
        
        response = self.client.post(vote_url, vote_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Should have only one vote record per user per session
        votes = Vote.objects.filter(debate_session=self.session, user=self.viewer)
        self.assertEqual(votes.count(), 1)
        self.assertEqual(votes.first().vote_type, 'opposition')

    def test_get_voting_results(self):
        """Test retrieving voting results."""
        # Create some votes
        Vote.objects.create(
            debate_session=self.session,
            user=self.viewer,
            vote_type='proposition'
        )
        
        results_url = reverse('voting-results', kwargs={'session_id': self.session.pk})
        response = self.client.get(results_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('proposition_votes', response.data)
        self.assertIn('opposition_votes', response.data)
        self.assertIn('total_votes', response.data)

    def test_vote_on_non_voting_session(self):
        """Test voting on session that's not in voting phase."""
        self.session.status = 'online'
        self.session.save()
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.viewer_token}')
        
        vote_url = reverse('submit-vote', kwargs={'session_id': self.session.pk})
        vote_data = {'vote_type': 'proposition'}
        
        response = self.client.post(vote_url, vote_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ModerationTestCase(APITestCase):
    """Test moderation functionality."""

    def setUp(self):
        """Set up test data."""
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpass123',
            role='student'
        )
        self.moderator = User.objects.create_user(
            username='moderator',
            email='moderator@example.com',
            password='testpass123',
            role='moderator'
        )
        
        self.student_token = RefreshToken.for_user(self.student).access_token
        self.moderator_token = RefreshToken.for_user(self.moderator).access_token
        
        self.topic = DebateTopic.objects.create(
            title='Test Topic',
            description='Test Description',
            category='Test',
            created_by=self.moderator
        )
        
        self.session = DebateSession.objects.create(
            topic=self.topic,
            moderator=self.moderator,
            scheduled_start=timezone.now() + timezone.timedelta(hours=1),
            duration_minutes=60,
            status='online'
        )
        
        # Add student as participant
        self.participation = Participation.objects.create(
            session=self.session,
            user=self.student,
            role='participant',
            side='proposition'
        )

    def test_mute_participant_as_moderator(self):
        """Test muting participant as moderator."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.moderator_token}')
        
        url = reverse('session-mute-participant', kwargs={'pk': self.session.pk})
        mute_data = {
            'user_id': self.student.pk,
            'reason': 'Inappropriate language'
        }
        
        response = self.client.post(url, mute_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.participation.refresh_from_db()
        self.assertTrue(self.participation.is_muted)

    def test_mute_participant_as_student_forbidden(self):
        """Test muting participant as student should be forbidden."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student_token}')
        
        url = reverse('session-mute-participant', kwargs={'pk': self.session.pk})
        mute_data = {
            'user_id': self.student.pk,
            'reason': 'Should not work'
        }
        
        response = self.client.post(url, mute_data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_remove_participant_as_moderator(self):
        """Test removing participant as moderator."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.moderator_token}')
        
        url = reverse('session-remove-participant', kwargs={'pk': self.session.pk})
        remove_data = {
            'user_id': self.student.pk,
            'reason': 'Violation of rules'
        }
        
        response = self.client.post(url, remove_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.participation.refresh_from_db()
        self.assertIsNotNone(self.participation.left_at)
        self.assertTrue(self.participation.was_removed)

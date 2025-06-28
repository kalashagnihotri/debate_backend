"""
Management command to create sample data for testing the debate platform.

This command creates sample users, topics, sessions, and other test data
that can be used for development and testing purposes.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from debates.models import DebateTopic, DebateSession, Message, Participation, Vote
from notifications.models import Notification

User = get_user_model()


class Command(BaseCommand):
    help = "Create sample data for testing the debate platform"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before creating sample data",
        )
        parser.add_argument(
            "--users-only",
            action="store_true",
            help="Load only user data",
        )
        parser.add_argument(
            "--skip-users",
            action="store_true",
            help="Skip loading user data",
        )

    def handle(self, *args, **options):
        """Create sample data for the debate platform."""

        if options["clear"]:
            self.stdout.write("Clearing existing data...")
            self.clear_data()

        if options["users_only"]:
            self.create_users()
            return

        # Create data in dependency order
        if not options["skip_users"]:
            self.create_users()

        self.create_topics()
        self.create_sessions()
        self.create_participation()
        self.create_messages()
        self.create_votes()
        self.create_notifications()

        self.stdout.write(self.style.SUCCESS("Successfully created sample data!"))

    def clear_data(self):
        """Clear existing sample data."""
        Vote.objects.all().delete()
        Message.objects.all().delete()
        Participation.objects.all().delete()
        DebateSession.objects.all().delete()
        DebateTopic.objects.all().delete()
        Notification.objects.all().delete()
        User.objects.filter(username__startswith="sample_").delete()
        self.stdout.write("Existing data cleared.")

    def create_users(self):
        """Create sample users."""
        self.stdout.write("Creating sample users...")

        # Create moderator
        moderator, created = User.objects.get_or_create(
            username="sample_moderator",
            defaults={
                "email": "moderator@example.com",
                "first_name": "Sample",
                "last_name": "Moderator",
                "role": "moderator",
                "is_staff": True,
            },
        )
        if created:
            moderator.set_password("samplepass123")
            moderator.save()

        # Create students
        students_data = [
            ("sample_student1", "Alice", "Johnson", "alice@example.com"),
            ("sample_student2", "Bob", "Smith", "bob@example.com"),
            ("sample_student3", "Carol", "Davis", "carol@example.com"),
        ]

        for username, first_name, last_name, email in students_data:
            student, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "role": "student",
                },
            )
            if created:
                student.set_password("samplepass123")
                student.save()

        self.stdout.write("Sample users created.")

    def create_topics(self):
        """Create sample debate topics."""
        self.stdout.write("Creating sample topics...")

        topics_data = [
            {
                "title": "Should Artificial Intelligence Development Be Regulated?",
                "description": "A debate about government regulation of AI development and deployment.",
                "category": "Technology",
            },
            {
                "title": "Is Remote Work More Effective Than Office Work?",
                "description": "Examining the productivity and benefits of remote vs office work.",
                "category": "Workplace",
            },
            {
                "title": "Should Social Media Platforms Be Held Liable for User Content?",
                "description": "Discussing platform responsibility for content moderation.",
                "category": "Technology",
            },
        ]

        moderator = User.objects.get(username="sample_moderator")

        for topic_data in topics_data:
            topic, created = DebateTopic.objects.get_or_create(
                title=topic_data["title"],
                defaults={
                    "description": topic_data["description"],
                    "category": topic_data["category"],
                    "created_by": moderator,
                },
            )

        self.stdout.write("Sample topics created.")

    def create_sessions(self):
        """Create sample debate sessions."""
        self.stdout.write("Creating sample sessions...")

        moderator = User.objects.get(username="sample_moderator")
        topics = DebateTopic.objects.all()[:2]

        # Create a completed session
        session1, created = DebateSession.objects.get_or_create(
            title="AI Regulation Discussion - Sample",
            defaults={
                "topic": topics[0],
                "moderator": moderator,
                "description": "Sample debate session on AI regulation",
                "scheduled_start": timezone.now() - timedelta(days=1),
                "duration_minutes": 60,
                "max_participants": 4,
                "status": "completed",
                "debate_started_at": timezone.now() - timedelta(days=1, minutes=30),
                "debate_ended_at": timezone.now() - timedelta(days=1, minutes=-30),
            },
        )

        # Create an upcoming session
        session2, created = DebateSession.objects.get_or_create(
            title="Remote Work Debate - Sample",
            defaults={
                "topic": topics[1],
                "moderator": moderator,
                "description": "Sample debate session on remote work",
                "scheduled_start": timezone.now() + timedelta(days=2),
                "duration_minutes": 90,
                "max_participants": 6,
                "status": "scheduled",
            },
        )

        self.stdout.write("Sample sessions created.")

    def create_participation(self):
        """Create sample participation records."""
        self.stdout.write("Creating sample participation...")

        session = DebateSession.objects.filter(status="completed").first()
        students = User.objects.filter(username__startswith="sample_student")[:2]

        if session and students:
            # Add participants
            Participation.objects.get_or_create(
                session=session,
                user=students[0],
                defaults={
                    "role": "participant",
                    "side": "proposition",
                    "joined_at": session.scheduled_start,
                    "is_participant": True,
                },
            )

            Participation.objects.get_or_create(
                session=session,
                user=students[1],
                defaults={
                    "role": "participant",
                    "side": "opposition",
                    "joined_at": session.scheduled_start,
                    "is_participant": True,
                },
            )

        self.stdout.write("Sample participation created.")

    def create_messages(self):
        """Create sample messages."""
        self.stdout.write("Creating sample messages...")

        session = DebateSession.objects.filter(status="completed").first()
        participants = User.objects.filter(
            participation__session=session, participation__role="participant"
        )

        if session and participants.exists():
            messages_data = [
                {
                    "content": "I believe AI regulation is essential for ethical development.",
                    "message_type": "argument",
                    "author": participants[0],
                },
                {
                    "content": "Excessive regulation could stifle innovation and progress.",
                    "message_type": "argument",
                    "author": participants[1],
                },
                {
                    "content": "However, we need safeguards to prevent potential misuse.",
                    "message_type": "rebuttal",
                    "author": participants[0],
                },
            ]

            for i, msg_data in enumerate(messages_data):
                Message.objects.get_or_create(
                    session=session,
                    author=msg_data["author"],
                    content=msg_data["content"],
                    defaults={
                        "message_type": msg_data["message_type"],
                        "timestamp": session.debate_started_at
                        + timedelta(minutes=i * 10),
                    },
                )

        self.stdout.write("Sample messages created.")

    def create_votes(self):
        """Create sample votes."""
        self.stdout.write("Creating sample votes...")

        session = DebateSession.objects.filter(status="completed").first()
        voter = User.objects.filter(username="sample_student3").first()

        if session and voter:
            Vote.objects.get_or_create(
                debate_session=session,
                voter=voter,
                defaults={
                    "vote_type": "WINNING_SIDE",
                    "winning_side": "proposition",
                    "created_at": session.debate_ended_at + timedelta(minutes=5),
                },
            )

        self.stdout.write("Sample votes created.")

    def create_notifications(self):
        """Create sample notifications."""
        self.stdout.write("Creating sample notifications...")

        students = User.objects.filter(username__startswith="sample_student")
        upcoming_session = DebateSession.objects.filter(status="scheduled").first()

        if students and upcoming_session:
            for student in students[:2]:
                Notification.objects.get_or_create(
                    user=student,
                    message=f'Debate session "{upcoming_session.title}" is scheduled for {upcoming_session.scheduled_start.strftime("%Y-%m-%d %H:%M")}',
                    defaults={
                        "type": "UPCOMING_DEBATE",
                        "is_read": False,
                    },
                )

        self.stdout.write("Sample notifications created.")

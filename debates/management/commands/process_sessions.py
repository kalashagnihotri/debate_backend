from datetime import timedelta

from debates.models import DebateSession, Notification
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Process automatic session state transitions"

    def handle(self, *args, **options):
        now = timezone.now()

        # Auto-start joining windows for scheduled sessions
        sessions_to_open = DebateSession.objects.filter(
            status="offline", scheduled_start__lte=now
        )

        for session in sessions_to_open:
            session.status = "open"
            session.joining_window_end = now + timedelta(minutes=5)
            session.save()

            self.stdout.write(
                self.style.SUCCESS(f"Started joining window for session {session.id}")
            )

            # Notify users
            self._notify_debate_starting(session)

        # Auto-transition from joining window to debate
        sessions_to_start = DebateSession.objects.filter(
            status="open", joining_window_end__lte=now
        )

        for session in sessions_to_start:
            session.status = "online"
            session.actual_start_time = now
            session.debate_end_time = now + timedelta(minutes=session.duration_minutes)
            session.save()

            self.stdout.write(
                self.style.SUCCESS(f"Started debate for session {session.id}")
            )

        # Auto-transition from debate to voting
        sessions_to_vote = DebateSession.objects.filter(
            status="online", debate_end_time__lte=now
        )

        for session in sessions_to_vote:
            session.status = "closed"
            session.voting_end_time = now + timedelta(minutes=10)
            session.save()

            self.stdout.write(
                self.style.SUCCESS(f"Started voting period for session {session.id}")
            )

            # Notify participants about voting
            self._notify_voting_started(session)

        # Auto-finish voting and calculate results
        sessions_to_finish = DebateSession.objects.filter(
            status="closed", voting_end_time__lte=now
        )

        for session in sessions_to_finish:
            session.status = "finished"
            session.save()

            self.stdout.write(self.style.SUCCESS(f"Finished session {session.id}"))

    def _notify_debate_starting(self, session):
        """Notify all registered users about debate starting"""
        from django.contrib.auth import get_user_model

        User = get_user_model()

        # For now, notify all active users - in production, this would be more targeted
        users = User.objects.filter(is_active=True)[:50]  # Limit to avoid spam

        notifications = [
            Notification(
                recipient=user,
                notification_type="debate_starting",
                title=f"Debate starting: {session.topic.title}",
                message=f'A debate on "{session.topic.title}" is starting! Join now during the 5-minute joining window.',
                session=session,
            )
            for user in users
        ]

        Notification.objects.bulk_create(notifications)

    def _notify_voting_started(self, session):
        """Notify session participants about voting"""
        participants = session.participants.all()

        notifications = [
            Notification(
                recipient=participant,
                notification_type="vote_reminder",
                title="Voting has started!",
                message=f'The debate on "{session.topic.title}" has ended. You have 10 minutes to vote.',
                session=session,
            )
            for participant in participants
        ]

        Notification.objects.bulk_create(notifications)

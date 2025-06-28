"""
Management command to load sample data for testing.

This command loads all the sample fixtures in the correct order
to maintain referential integrity.
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Load sample data fixtures for testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Flush database before loading fixtures",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write("Flushing database...")
            call_command("flush", "--noinput")

        self.stdout.write("Loading sample data fixtures...")

        # Load fixtures in dependency order
        fixtures = [
            "sample_users.json",
            "sample_topics.json",
            "sample_sessions.json",
            "sample_participation.json",
            "sample_messages.json",
            "sample_votes.json",
            "sample_notifications.json",
        ]

        for fixture in fixtures:
            try:
                self.stdout.write(f"Loading {fixture}...")
                call_command("loaddata", fixture)
                self.stdout.write(self.style.SUCCESS(f"Successfully loaded {fixture}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error loading {fixture}: {e}"))

        self.stdout.write(self.style.SUCCESS("Successfully loaded all sample data!"))

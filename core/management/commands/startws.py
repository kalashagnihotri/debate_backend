import os
import subprocess
import sys

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Start Daphne WebSocket server with network access'

    def add_arguments(self, parser):
        parser.add_argument(
            '--localhost',
            action='store_true',
            help='Start server on localhost only (127.0.0.1)',
        )

    def handle(self, *args, **options):
        # Get configuration from settings
        port = settings.DAPHNE_PORT
        host = '127.0.0.1' if options['localhost'] else settings.HOST

        self.stdout.write(
            self.style.SUCCESS('\1')
        )
        self.stdout.write(
            self.style.WARNING(f'📍 WebSocket will be available at: ws://{host}:{port}')
        )

        if not options['localhost']:
            local_ip = settings.LOCAL_IP
            self.stdout.write(
                self.style.HTTP_INFO(f'🌐 Network WebSocket URL: ws://{local_ip}:{port}')
            )

        # Start Daphne server
        cmd = [
            'daphne',
            '-b', host,
            '-p', str(port),
            'onlineDebatePlatform.asgi:application'
        ]

        try:
            subprocess.run(cmd, check=True)
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(
                    '❌ Daphne not found. Make sure it\'s installed in your virtual environment.')
            )
            self.stdout.write(
                self.style.WARNING('💡 Run: pip install daphne')
            )
            sys.exit(1)
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.SUCCESS('✅ WebSocket server stopped.')
            )

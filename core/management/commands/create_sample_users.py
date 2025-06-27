"""
Create sample users with properly hashed passwords.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from notifications.models import Notification
from debates.models import DebateTopic, DebateSession, Participation, Message, DebateVote, Vote

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data with proper password hashing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample users with hashed passwords...')
        
        # Create users with hashed passwords
        users_data = [
            {
                'username': 'admin_user',
                'email': 'admin@debateplatform.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'moderator',
                'password': 'AdminPass123!',
                'is_staff': True
            },
            {
                'username': 'moderator_alice',
                'email': 'alice@debateplatform.com', 
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'role': 'moderator',
                'password': 'AlicePass123!'
            },
            {
                'username': 'student_bob',
                'email': 'bob@university.edu',
                'first_name': 'Bob',
                'last_name': 'Smith', 
                'role': 'student',
                'password': 'BobPass123!'
            },
            {
                'username': 'student_charlie',
                'email': 'charlie@university.edu',
                'first_name': 'Charlie',
                'last_name': 'Brown',
                'role': 'student', 
                'password': 'CharliePass123!'
            },
            {
                'username': 'student_diana',
                'email': 'diana@university.edu',
                'first_name': 'Diana',
                'last_name': 'Wilson',
                'role': 'student',
                'password': 'DianaPass123!'
            }
        ]
        
        created_users = {}
        for user_data in users_data:
            password = user_data.pop('password')
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(f'Created user: {user.username}')
            else:
                self.stdout.write(f'User already exists: {user.username}')
            created_users[user_data['username']] = user
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample users!')
        )
        
        # Print login credentials for testing
        self.stdout.write('\n' + '='*50)
        self.stdout.write('TEST LOGIN CREDENTIALS:')
        self.stdout.write('='*50)
        for user_data in users_data:
            username = user_data['username']
            original_password = {
                'admin_user': 'AdminPass123!',
                'moderator_alice': 'AlicePass123!',
                'student_bob': 'BobPass123!',
                'student_charlie': 'CharliePass123!',
                'student_diana': 'DianaPass123!'
            }[username]
            self.stdout.write(f'{username}: {original_password}')
        self.stdout.write('='*50)

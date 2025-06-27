# Sample Data Fixtures

This directory contains sample data fixtures for testing the Online Debate Platform.

## Fixtures Included

### 1. `sample_users.json`
- 5 test users (1 admin, 1 moderator, 3 students)
- Includes user profiles with realistic bio information
- Users have different roles for testing authorization

### 2. `sample_topics.json`
- 5 debate topics across different categories
- Topics include: AI regulation, remote work, social media liability, online education, cryptocurrency
- Created by different moderators to test ownership

### 3. `sample_sessions.json`
- 3 debate sessions in different states
- One completed session, two scheduled sessions
- Different durations and participant limits

### 4. `sample_participation.json`
- Participation records linking users to sessions
- Includes both participants and observers
- Shows different debate sides (proposition/opposition)

### 5. `sample_messages.json`
- 6 sample messages from a completed debate
- Different message types: argument, rebuttal, question, closing
- Demonstrates realistic debate flow

### 6. `sample_votes.json`
- Sample voting data for completed sessions
- Includes both DebateVote and Vote model entries
- Shows voting for winning side

### 7. `sample_notifications.json`
- 5 notifications of different types
- Mix of read and unread notifications
- Various notification types: upcoming debates, voting, new topics

## Loading Sample Data

### Method 1: Using Management Command (Recommended)
```bash
# Load all sample data
python manage.py load_sample_data

# Flush database and load fresh data
python manage.py load_sample_data --flush
```

### Method 2: Using Django loaddata
```bash
# Load fixtures individually (in order)
python manage.py loaddata sample_users.json
python manage.py loaddata sample_topics.json
python manage.py loaddata sample_sessions.json
python manage.py loaddata sample_participation.json
python manage.py loaddata sample_messages.json
python manage.py loaddata sample_votes.json
python manage.py loaddata sample_notifications.json
```

### Method 3: Create Users with Proper Passwords
```bash
# Create users with hashed passwords (for authentication testing)
python manage.py create_sample_users
```

## Test User Credentials

When using the `create_sample_users` command, the following credentials are available:

- **admin_user**: AdminPass123! (Moderator + Staff)
- **moderator_alice**: AlicePass123! (Moderator)
- **student_bob**: BobPass123! (Student)
- **student_charlie**: CharliePass123! (Student)
- **student_diana**: DianaPass123! (Student)

## Usage in Tests

These fixtures can be used in automated tests:

```python
from django.test import TestCase
from django.core.management import call_command

class DebateTestCase(TestCase):
    def setUp(self):
        # Load sample data for testing
        call_command('load_sample_data')
        
    def test_debate_functionality(self):
        # Your test code here
        pass
```

## Data Relationships

The sample data maintains proper referential integrity:

1. **Users** → **Profiles** (One-to-One)
2. **Users** → **Topics** (Created by moderators)
3. **Topics** → **Sessions** (Each session has a topic)
4. **Users** → **Sessions** (Moderator relationship)
5. **Users** + **Sessions** → **Participation** (Many-to-Many through)
6. **Users** + **Sessions** → **Messages** (Messages in sessions)
7. **Users** + **Sessions** → **Votes** (Voting on sessions)
8. **Users** → **Notifications** (User-specific notifications)

## Customization

To create your own fixtures:

1. Create objects in Django admin or shell
2. Export using: `python manage.py dumpdata app.model --indent=2 > fixtures/custom_data.json`
3. Edit the JSON file as needed
4. Load using: `python manage.py loaddata custom_data.json`

## Notes

- The JSON fixtures use placeholder password hashes
- For authentication testing, use the `create_sample_users` command
- All timestamps are in UTC format
- Foreign key relationships use primary keys (integers)
- The data represents a realistic debate platform scenario

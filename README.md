# Online Debate Platform Backend

A production-ready Django REST API backend for real-time debate sessions with WebSocket support.

## Quick Start

### Setup & Installation
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start Django API server
python manage.py startapi --localhost

# Start WebSocket server (in separate terminal)
python manage.py startws --localhost
```

## Servers
- Django API: http://localhost:8000
- WebSocket: http://localhost:8001
- Admin Panel: http://localhost:8000/admin/
- API Documentation: http://localhost:8000/swagger/

## Interactive API Documentation

This backend provides comprehensive interactive API documentation using Swagger/OpenAPI.

### Access API Documentation
- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/

### Swagger Features
- **Interactive Testing** - Test API endpoints directly from the browser
- **Authentication Support** - Built-in JWT token authentication
- **Request/Response Examples** - Complete payload examples
- **Schema Validation** - Real-time request validation
- **Endpoint Filtering** - Filter by tags and operations

### Using Swagger UI
1. Navigate to http://localhost:8000/swagger/
2. Click "Authorize" button in the top right
3. Enter your JWT token: `Bearer YOUR_ACCESS_TOKEN`
4. Explore and test API endpoints interactively

### API Schema Export
Download the OpenAPI schema in various formats:
- **JSON**: http://localhost:8000/swagger.json
- **YAML**: http://localhost:8000/swagger.yaml

### API Data Models

#### User Model
```json
{
  "id": 1,
  "username": "debater1",
  "email": "debater1@example.com",
  "role": "student",
  "date_joined": "2025-06-27T10:00:00Z"
}
```

#### Debate Topic Model
```json
{
  "id": 1,
  "title": "Should AI replace human teachers?",
  "description": "A debate about the role of AI in education",
  "category": "Education",
  "created_at": "2025-06-27T10:00:00Z"
}
```

#### Debate Session Model
```json
{
  "id": 1,
  "topic": {
    "id": 1,
    "title": "Should AI replace human teachers?"
  },
  "moderator": {
    "id": 1,
    "username": "moderator1"
  },
  "status": "online",
  "scheduled_start": "2025-06-28T14:00:00Z",
  "duration_minutes": 60,
  "participant_count": 4,
  "viewer_count": 12,
  "can_join_as_participant": false,
  "can_join_as_viewer": true,
  "is_voting_active": false
}
```

#### Message Model
```json
{
  "id": 1,
  "session": 1,
  "author": {
    "id": 2,
    "username": "debater1"
  },
  "content": "I strongly believe that AI cannot replace human teachers because...",
  "message_type": "argument",
  "timestamp": "2025-06-28T14:15:30Z"
}
```

#### Vote Model
```json
{
  "id": 1,
  "user": {
    "id": 3,
    "username": "viewer1"
  },
  "debate_session": 1,
  "vote_type": "proposition",
  "created_at": "2025-06-28T15:00:00Z"
}
```

## API Documentation

### Authentication
All API endpoints require JWT authentication except registration and login.

#### Get JWT Token
```bash
curl -X POST http://localhost:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Use Token in Requests
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" http://localhost:8000/api/v1/users/
```

### API Endpoints

#### Authentication Endpoints
- `POST /api/v1/token/` - Obtain JWT access token
- `POST /api/v1/token/refresh/` - Refresh JWT token

#### User Management
- `POST /api/v1/users/register/` - User registration
- `GET /api/v1/users/` - List all users (authenticated)
- `GET /api/v1/users/{id}/` - Get user details
- `GET /api/v1/users/profiles/me/` - Get current user profile
- `PATCH /api/v1/users/profiles/update_profile/` - Update user profile

#### Debate Topics
- `GET /api/v1/debates/topics/` - List all topics (public)
- `POST /api/v1/debates/topics/` - Create new topic (moderator only)
- `GET /api/v1/debates/topics/{id}/` - Get topic details
- `PUT /api/v1/debates/topics/{id}/` - Update topic (moderator only)
- `DELETE /api/v1/debates/topics/{id}/` - Delete topic (moderator only)

#### Debate Sessions
- `GET /api/v1/debates/sessions/` - List all sessions (public)
- `POST /api/v1/debates/sessions/` - Create new session (moderator only)
- `GET /api/v1/debates/sessions/{id}/` - Get session details
- `PUT /api/v1/debates/sessions/{id}/` - Update session (moderator only)
- `DELETE /api/v1/debates/sessions/{id}/` - Delete session (moderator only)

#### Session Participation
- `POST /api/v1/debates/sessions/{id}/join/` - Join session as participant/viewer
- `POST /api/v1/debates/sessions/{id}/leave/` - Leave session
- `GET /api/v1/debates/sessions/{id}/participants/` - Get session participants
- `GET /api/v1/debates/sessions/{id}/status/` - Get real-time session status

#### Session Control (Moderator Only)
- `POST /api/v1/debates/sessions/{id}/start_joining/` - Open joining phase
- `POST /api/v1/debates/sessions/{id}/start_debate/` - Start debate phase
- `POST /api/v1/debates/sessions/{id}/start_voting/` - Start voting phase
- `POST /api/v1/debates/sessions/{id}/end_session/` - End session

#### Moderation Actions (Moderator Only)
- `POST /api/v1/debates/sessions/{id}/mute_participant/` - Mute participant
- `POST /api/v1/debates/sessions/{id}/warn_participant/` - Warn participant
- `POST /api/v1/debates/sessions/{id}/remove_participant/` - Remove participant
- `GET /api/v1/debates/moderation-actions/` - List moderation actions

#### Messages
- `GET /api/v1/debates/messages/?session_pk={id}` - Get session messages
- `POST /api/v1/debates/messages/` - Send message (participants only)

#### Voting System
- `POST /api/v1/debates/sessions/{id}/vote/` - Submit vote (viewers only)
- `GET /api/v1/debates/sessions/{id}/votes/` - Get voting results
- `GET /api/v1/debates/sessions/{id}/voting_results/` - Get detailed voting analytics

#### Session Analytics
- `GET /api/v1/debates/sessions/{id}/analytics/` - Get session analytics
- `GET /api/v1/debates/sessions/{id}/transcript/` - Get session transcript

#### Notifications
- `GET /api/v1/notifications/` - Get user notifications
- `POST /api/v1/notifications/mark_as_read/` - Mark notifications as read
- `GET /api/v1/notifications/stats/` - Get notification statistics

### HTTP Status Codes
- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `204 No Content` - Request successful, no content returned
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict (e.g., already joined session)
- `500 Internal Server Error` - Server error

### Error Response Format
All API errors follow a consistent format:
```json
{
  "error": "Detailed error message",
  "field_errors": {
    "field_name": ["Field-specific error messages"]
  },
  "status_code": 400
}
```

Example validation error:
```json
{
  "error": "Validation failed",
  "field_errors": {
    "username": ["This field is required."],
    "password": ["Password must be at least 8 characters long."]
  },
  "status_code": 400
}
```

### Rate Limiting
API endpoints may be rate-limited:
- Authentication endpoints: 5 requests per minute
- Other endpoints: 60 requests per minute
- WebSocket connections: 10 concurrent connections per user

### Pagination
List endpoints support pagination:
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/v1/debates/sessions/?page=2",
  "previous": null,
  "results": [...] 
}
```

Query parameters:
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)

### API Usage Examples

#### 1. Complete Authentication Flow
```bash
# Register new user
curl -X POST http://localhost:8000/api/v1/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "debater1",
    "email": "debater1@example.com",
    "password": "securepass123",
    "role": "student"
  }'

# Get JWT token
curl -X POST http://localhost:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "debater1",
    "password": "securepass123"
  }'

# Response: {"access": "eyJ...", "refresh": "eyJ..."}
```

#### 2. Topic and Session Management
```bash
# Create debate topic (moderator only)
curl -X POST http://localhost:8000/api/v1/debates/topics/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Should AI replace human teachers?",
    "description": "A debate about the role of AI in education",
    "category": "Education"
  }'

# Create debate session (moderator only)
curl -X POST http://localhost:8000/api/v1/debates/sessions/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic_id": 1,
    "scheduled_start": "2025-06-28T14:00:00Z",
    "duration_minutes": 60
  }'
```

#### 3. Session Participation Flow
```bash
# Join as participant
curl -X POST http://localhost:8000/api/v1/debates/sessions/1/join/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "participant",
    "side": "proposition"
  }'

# Check session status
curl http://localhost:8000/api/v1/debates/sessions/1/status/

# Get participants
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/debates/sessions/1/participants/
```

#### 4. Messaging and Communication
```bash
# Send debate message
curl -X POST http://localhost:8000/api/v1/debates/messages/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session": 1,
    "content": "I strongly believe that AI cannot replace human teachers because emotional intelligence is crucial for effective learning.",
    "message_type": "argument"
  }'

# Get session messages
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/debates/messages/?session_pk=1"
```

#### 5. Voting System
```bash
# Submit vote (viewers only)
curl -X POST http://localhost:8000/api/v1/debates/sessions/1/vote/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vote_type": "proposition"
  }'

# Get voting results
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/debates/sessions/1/voting_results/
```

#### 6. Moderation Actions (Moderator Only)
```bash
# Mute participant
curl -X POST http://localhost:8000/api/v1/debates/sessions/1/mute_participant/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 5,
    "reason": "Inappropriate language"
  }'

# Remove participant
curl -X POST http://localhost:8000/api/v1/debates/sessions/1/remove_participant/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 5,
    "reason": "Violation of debate rules"
  }'
```

#### 7. Analytics and Reporting
```bash
# Get session analytics
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/debates/sessions/1/analytics/

# Get session transcript
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/debates/sessions/1/transcript/

# Get user profile with statistics
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/users/profiles/me/
```

#### 8. Notifications Management
```bash
# Get user notifications
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/notifications/

# Mark notifications as read
curl -X POST http://localhost:8000/api/v1/notifications/mark_as_read/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notification_ids": [1, 2, 3]
  }'
```

#### 7. Get Session Status
```bash
curl http://localhost:8000/api/v1/debates/sessions/1/status/
```

Response:
```json
{
  "phase": "online",
  "canJoin": false,
  "canChat": true,
  "canVote": false,
  "participantCount": 4,
  "viewerCount": 12,
  "messageCount": 23
}
```

### API Testing with Postman

1. **Import OpenAPI Schema**
   - Download schema: http://localhost:8000/swagger.json
   - Import into Postman: File → Import → Link
   - Paste the swagger.json URL

2. **Set up Environment Variables**
   ```
   BASE_URL: http://localhost:8000
   ACCESS_TOKEN: (obtain from /api/v1/token/ endpoint)
   ```

3. **Configure Authorization**
   - Type: Bearer Token
   - Token: {{ACCESS_TOKEN}}

### WebSocket Connection

Connect to WebSocket for real-time updates:
```javascript
// Connect to specific debate session
const socket = new WebSocket('ws://localhost:8001/ws/debate/1/');

// Handle connection events
socket.onopen = function(event) {
    console.log('Connected to debate session');
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
    
    // Handle different message types
    switch(data.type) {
        case 'chat_message':
            displayMessage(data.message);
            break;
        case 'user_joined':
            updateParticipantsList(data.user);
            break;
        case 'session_status_update':
            updateSessionStatus(data.status);
            break;
        case 'vote_update':
            updateVotingResults(data.votes);
            break;
    }
};

socket.onerror = function(error) {
    console.error('WebSocket error:', error);
};

socket.onclose = function(event) {
    console.log('Disconnected from debate session');
};

// Send message via WebSocket
function sendMessage(content) {
    socket.send(JSON.stringify({
        'type': 'chat_message',
        'message': content,
        'message_type': 'argument'
    }));
}

// Send voting data
function submitVote(voteType) {
    socket.send(JSON.stringify({
        'type': 'vote',
        'vote_type': voteType
    }));
}
```

#### WebSocket Message Types
- `chat_message` - New message posted
- `user_joined` - User joined session
- `user_left` - User left session
- `session_status_update` - Session phase changed
- `vote_update` - Voting results updated
- `moderation_action` - Moderation action taken
- `participant_muted` - Participant muted/unmuted

## Environment Configuration

Create a `.env` file in the project root:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

## Production Deployment

### Requirements
- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- ASGI server (e.g., Daphne, Uvicorn)

### Environment Variables
```env
DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:password@host:port/database
REDIS_URL=redis://host:port/db
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourfrontend.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Deployment Steps
1. Set up PostgreSQL database
2. Configure Redis server
3. Set environment variables
4. Run migrations: `python manage.py migrate`
5. Collect static files: `python manage.py collectstatic`
6. Start ASGI server: `daphne -b 0.0.0.0 -p 8000 onlineDebatePlatform.asgi:application`

## Technical Architecture

### Backend Stack
- **Django 4.2** - Web framework
- **Django REST Framework** - API framework
- **Channels** - WebSocket support
- **Redis** - Channel layer backend
- **PostgreSQL** - Production database
- **JWT** - Authentication tokens

### Key Features
- **RESTful API** - Standard HTTP endpoints
- **Real-time WebSocket** - Live chat and updates
- **Role-based Permissions** - Student/Moderator access control
- **Session Lifecycle Management** - Automated debate flow
- **Comprehensive Moderation** - Tools for session control
- **Voting System** - Democratic outcome determination
- **Analytics & Reporting** - Session statistics and insights

### Database Models
- **User** - Authentication and profile
- **DebateTopic** - Debate subjects
- **DebateSession** - Active debate instances
- **Participation** - User session involvement
- **Message** - Chat messages and arguments
- **Vote** - User voting records
- **ModerationAction** - Moderation history
- **Notification** - User notifications

### API Design Patterns
- Class-based views using DRF ViewSets
- Model serializers for data validation
- JWT token authentication
- Permission classes for authorization
- Custom management commands for server control

## Testing

This project includes comprehensive tests for all critical endpoints and functionality.

### Running Tests

#### Option 1: Using PowerShell Script (Recommended for Windows)
```powershell
# Run all tests with coverage
.\run_tests.ps1
```

#### Option 2: Using Django Test Runner
```bash
# Activate virtual environment first
.\.venv\Scripts\Activate.ps1

# Run all tests
python manage.py test --settings=onlineDebatePlatform.test_settings

# Run specific app tests
python manage.py test users.tests --settings=onlineDebatePlatform.test_settings
python manage.py test debates.tests --settings=onlineDebatePlatform.test_settings
python manage.py test notifications.tests --settings=onlineDebatePlatform.test_settings
```

#### Option 3: Using pytest (if installed)
```bash
# Install pytest-django if not already installed
pip install pytest-django

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

### Test Coverage

The test suite covers:

#### **User Authentication & Authorization**
- User registration with validation
- JWT token authentication
- Login/logout functionality
- Role-based permissions (Student vs Moderator)
- Profile management

#### **Debate Topics**
- Topic creation (moderator only)
- Topic listing (public access)
- Topic details retrieval
- Topic updates and deletion
- Permission enforcement

#### **Debate Sessions**
- Session creation and management
- Session lifecycle (joining → debate → voting → ended)
- Participant management
- Session status tracking
- Real-time session updates

#### **Messaging System**
- Message sending during debates
- Message retrieval and filtering
- Participant-only messaging
- Message type validation

#### **Voting System**
- Vote submission (viewers only)
- Vote result calculation
- Duplicate vote handling
- Voting phase restrictions

#### **Moderation Tools**
- Participant muting/unmuting
- Participant warnings
- Participant removal
- Moderation action logging

#### **Notification System**
- Notification creation and delivery
- Mark as read functionality
- User-specific notification filtering
- Notification statistics

#### **Integration Tests**
- Complete debate workflow
- Authentication flows
- Permission enforcement
- Data consistency checks

### Test Structure

```
tests/
├── __init__.py              # Integration tests
├── conftest.py             # Test configuration
└── test_core.py            # Core functionality tests

users/
└── tests.py                # User-related tests

debates/
└── tests.py                # Debate functionality tests

notifications/
└── tests.py                # Notification tests
```

### Test Configuration

Tests use a separate configuration (`test_settings.py`) that:
- Uses SQLite in-memory database for speed
- Disables migrations for faster test runs
- Uses dummy cache and channel layers
- Configures fast password hashing
- Disables unnecessary logging

### Continuous Integration

The project includes GitHub Actions workflow (`.github/workflows/tests.yml`) that:
- Tests against multiple Python versions (3.9, 3.10, 3.11)
- Sets up PostgreSQL and Redis services
- Runs full test suite with coverage
- Performs code linting and formatting checks
- Uploads coverage reports to Codecov

### Test Commands Quick Reference

```bash
# Run all tests
python manage.py test --settings=onlineDebatePlatform.test_settings

# Run tests with coverage
coverage run --source='.' manage.py test --settings=onlineDebatePlatform.test_settings
coverage report
coverage html

# Run specific test class
python manage.py test users.tests.UserRegistrationTestCase --settings=onlineDebatePlatform.test_settings

# Run specific test method
python manage.py test users.tests.UserRegistrationTestCase.test_user_registration_success --settings=onlineDebatePlatform.test_settings

# Run tests with verbose output
python manage.py test --verbosity=2 --settings=onlineDebatePlatform.test_settings
```

### Expected Test Results

When running the complete test suite, you should see:
- **100+ test cases** covering all critical functionality
- **High test coverage** (>90%) across all modules
- **Integration tests** verifying complete workflows
- **Permission tests** ensuring proper access control
- **Error handling tests** for edge cases

## Testing

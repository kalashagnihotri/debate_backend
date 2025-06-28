# Online Debate Platform Backend

A production-ready Django REST API backend for real-time debate sessions with WebSocket support.

## 🚀 Recent Updates (June 2025)

### WebSocket Connectivity Fixes (June 29, 2025)
- **Fixed Message Model Import Issue**: Resolved "Message() got unexpected keyword arguments: 'author'" error by explicitly importing the correct Message model
- **Enhanced URL Routing**: Added support for both `/ws/debate/` and `/ws/debates/` WebSocket patterns for backward compatibility
- **Improved Error Handling**: Fixed invalid WebSocket close codes (now using valid 4000-4999 range)
- **Connection Stability**: Enhanced participant management and real-time messaging reliability
- **Database Schema Alignment**: Ensured Message model uses `user` field instead of deprecated `author` field

### Code Quality Improvements
- **PEP 8 Compliance**: All code formatted with Black for consistent styling
- **Explicit Imports**: Updated consumer imports to prevent model confusion between message.py and message_models.py
- **Error Handling**: Better exception handling in WebSocket consumers with proper close codes
- **Import Clarity**: Fixed ambiguous imports in participant management consumer

### Developer Experience
- **Enhanced Documentation**: Updated README with troubleshooting for common WebSocket issues
- **Improved Debugging**: Better logging and error messages for WebSocket connections
- **Connection Testing**: Enhanced demo page for testing real-time features
- **Migration Support**: Database migrations ensure proper Message model schema

## Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 12+ (recommended for production)
- Redis 6+ (for WebSocket support and caching)
- Git

### 1. Clone and Setup
```bash
git clone <your-repository-url>
cd debate_backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
# Copy environment template
copy .env.example .env

# Edit .env file with your settings
# Minimum required:
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://debate_user:password@localhost:5432/debate_platform
REDIS_URL=redis://localhost:6379/0
```

### 3. Database Setup

#### PostgreSQL Setup (Recommended)
```bash
# Install PostgreSQL
# Windows: Download from https://www.postgresql.org/download/windows/
# Create database and user
psql -U postgres
CREATE DATABASE debate_platform;
CREATE USER debate_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE debate_platform TO debate_user;
\q

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata fixtures/sample_*.json
```

#### SQLite Setup (Development Only)
```bash
# Update .env file
DATABASE_URL=sqlite:///db.sqlite3

# Run migrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Start the Servers

#### Option A: Using the Batch File (Windows)
```bash
# Double-click or run:
start_servers.bat
```

#### Option B: Manual Startup
```bash
# Terminal 1: Django API Server
python manage.py runserver localhost:8000

# Terminal 2: WebSocket Server (Daphne)
daphne -b localhost -p 8001 onlineDebatePlatform.asgi:application
```

### 5. Access the Application

- **Frontend Demo**: http://localhost:8000/demo/
- **API Documentation**: http://localhost:8000/swagger/
- **Admin Panel**: http://localhost:8000/admin/
- **API Base URL**: http://localhost:8000/api/

## 🎯 WebSocket Demo

The platform includes a complete frontend demo showcasing real-time WebSocket functionality:

### Features Demonstrated
- **Real-time Messaging**: Live chat with instant delivery
- **User Authentication**: JWT-based secure connections  
- **Participant Management**: Live participant lists and status
- **Typing Indicators**: Real-time typing notifications
- **Connection Management**: Auto-reconnection and heartbeat
- **Session Updates**: Live session status and notifications

### Demo Usage
1. Navigate to http://localhost:8000/demo/
2. Register a new account or login
3. Connect to a debate session (default: Session ID 1)
4. Test real-time messaging and WebSocket features
5. Use multiple browser tabs to simulate multiple users

### For Developers
The demo includes:
- Complete WebSocket client implementation
- API integration examples
- Connection resilience testing
- Comprehensive error handling
- Real-time debugging tools

See `frontend/README.md` for detailed technical documentation.

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

### Development Environment
Create a `.env` file in the project root for local development:

**PostgreSQL Configuration (Recommended):**
```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=postgresql://debate_user:your_password@localhost:5432/debate_platform
# Alternative format:
# DB_NAME=debate_platform
# DB_USER=debate_user
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Server Ports
DJANGO_PORT=8000
DAPHNE_PORT=8001
FRONTEND_PORT=3000
HOST=0.0.0.0

# CORS Configuration
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

**SQLite Configuration (Development Only):**
```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database Configuration (SQLite fallback)
DATABASE_URL=sqlite:///db.sqlite3

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Server Ports
DJANGO_PORT=8000
DAPHNE_PORT=8001
FRONTEND_PORT=3000
HOST=0.0.0.0

# CORS Configuration
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Test Environment
For running tests, the application automatically uses appropriate database settings. The GitHub Actions workflow is configured to use PostgreSQL for testing to match production.

### Database Configuration Notes

#### PostgreSQL Setup
1. **Install PostgreSQL**: Download from [postgresql.org](https://www.postgresql.org/download/)
2. **Create Database**:
   ```sql
   CREATE DATABASE debate_platform;
   CREATE USER debate_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE debate_platform TO debate_user;
   ALTER USER debate_user CREATEDB;  -- For running tests
   ```
3. **Update .env file** with your database credentials

#### Database URL Formats
```env
# PostgreSQL
DATABASE_URL=postgresql://username:password@host:port/database

# PostgreSQL with SSL
DATABASE_URL=postgresql://username:password@host:port/database?sslmode=require

# SQLite (relative path)
DATABASE_URL=sqlite:///db.sqlite3

# SQLite (absolute path)
DATABASE_URL=sqlite:////absolute/path/to/db.sqlite3
```

#### Redis Setup
Redis is used for WebSocket channels and caching:
```bash
# Install Redis (Windows - using chocolatey)
choco install redis-64

# Or download from: https://redis.io/download

# Start Redis server
redis-server

# Test Redis connection
redis-cli ping
```

## Production Deployment

### Requirements
- Python 3.9+
- PostgreSQL 12+ (required for production)
- Redis 6+ (required for WebSocket support)
- ASGI server (e.g., Daphne, Uvicorn, Gunicorn with uvicorn workers)

### Production Environment Variables
```env
# Django Settings
DEBUG=False
SECRET_KEY=your-very-secure-production-secret-key

# Database Configuration (PostgreSQL required)
DATABASE_URL=postgresql://username:password@host:port/database
# For managed services like AWS RDS, Azure Database, etc.:
# DATABASE_URL=postgresql://username:password@your-db-host.amazonaws.com:5432/debate_platform

# Redis Configuration
REDIS_URL=redis://host:port/db
# For managed Redis services:
# REDIS_URL=redis://your-redis-host.amazonaws.com:6379/0

# Security Settings
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,api.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourfrontend.com,https://www.yourfrontend.com

# Server Configuration
DJANGO_PORT=8000
DAPHNE_PORT=8001
HOST=0.0.0.0

# Email Configuration (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Static Files (for production)
STATIC_ROOT=/var/www/static/
MEDIA_ROOT=/var/www/media/
```

### Deployment Steps

#### 1. Server Preparation
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python, PostgreSQL, Redis
sudo apt install python3.9 python3-pip python3-venv postgresql postgresql-contrib redis-server

# Start services
sudo systemctl start postgresql
sudo systemctl start redis-server
sudo systemctl enable postgresql
sudo systemctl enable redis-server
```

#### 2. Database Setup
```bash
# Switch to PostgreSQL user
sudo -u postgres psql

# Create database and user
CREATE DATABASE debate_platform;
CREATE USER debate_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE debate_platform TO debate_user;
ALTER USER debate_user CREATEDB;
\q
```

#### 3. Application Deployment
```bash
# Clone repository
git clone your-repository-url
cd debate_backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with production values

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Test the setup
python manage.py check --deploy
```

#### 4. Process Management (using systemd)

Create service files for Django and Daphne:

**Django API Service** (`/etc/systemd/system/debate-api.service`):
```ini
[Unit]
Description=Debate Platform Django API
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/debate_backend
Environment=PATH=/path/to/debate_backend/.venv/bin
EnvironmentFile=/path/to/debate_backend/.env
ExecStart=/path/to/debate_backend/.venv/bin/python manage.py startapi
Restart=always

[Install]
WantedBy=multi-user.target
```

**WebSocket Service** (`/etc/systemd/system/debate-ws.service`):
```ini
[Unit]
Description=Debate Platform WebSocket Server
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/debate_backend
Environment=PATH=/path/to/debate_backend/.venv/bin
EnvironmentFile=/path/to/debate_backend/.env
ExecStart=/path/to/debate_backend/.venv/bin/python manage.py startws
Restart=always

[Install]
WantedBy=multi-user.target
```

**Start services:**
```bash
sudo systemctl daemon-reload
sudo systemctl start debate-api
sudo systemctl start debate-ws
sudo systemctl enable debate-api
sudo systemctl enable debate-ws
```

#### 5. Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Django API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket connections
    location /ws/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /var/www/static/;
        expires 30d;
    }

    # Media files
    location /media/ {
        alias /var/www/media/;
        expires 30d;
    }
}
```

### Docker Deployment (Alternative)

**Dockerfile:**
```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000 8001

CMD ["python", "manage.py", "startapi"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: debate_platform
      POSTGRES_USER: debate_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine

  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgresql://debate_user:secure_password@db:5432/debate_platform
      - REDIS_URL=redis://redis:6379/0

volumes:
  postgres_data:
```

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

## Troubleshooting

### Database Issues

#### PostgreSQL Connection Errors
```bash
# Error: "Could not connect to server: Connection refused"
# Solution: Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL if not running
sudo systemctl start postgresql

# Check PostgreSQL configuration
sudo -u postgres psql -c "SELECT version();"
```

#### Database Authentication Failed
```bash
# Error: "FATAL: password authentication failed"
# Solution: Reset user password
sudo -u postgres psql
ALTER USER debate_user PASSWORD 'your_new_password';
\q

# Update .env file with new password
DATABASE_URL=postgresql://debate_user:your_new_password@localhost:5432/debate_platform
```

#### Migration Errors
```bash
# Error: "relation does not exist" or SQL syntax errors
# Solution: Check database type and migration compatibility

# For PostgreSQL-specific migrations failing on SQLite:
# Ensure you're using PostgreSQL for both development and testing

# Reset migrations (WARNING: This will delete all data)
python manage.py migrate debates zero
python manage.py migrate users zero
python manage.py migrate notifications zero
python manage.py migrate
```

### Environment Variable Issues

#### Missing .env File
```bash
# Error: Environment variables not loaded
# Solution: Create .env file in project root
cp .env.example .env

# Edit with your actual values
nano .env
```

#### Invalid SECRET_KEY
```bash
# Error: "ImproperlyConfigured: The SECRET_KEY setting must not be empty"
# Solution: Generate a new secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Add to .env file
SECRET_KEY=your-generated-secret-key-here
```

#### Port Already in Use
```bash
# Error: "Address already in use" or "Port 8000 is already in use"
# Solution: Kill existing processes or use different ports

# Find process using port 8000
netstat -tulpn | grep :8000

# Kill specific process
kill -9 <process_id>

# Or use different ports in .env
DJANGO_PORT=8080
DAPHNE_PORT=8081
```

### Redis Connection Issues

#### Redis Server Not Running
```bash
# Error: "ConnectionError: Error 111 connecting to localhost:6379"
# Solution: Start Redis server

# On Ubuntu/Debian
sudo systemctl start redis-server

# On Windows (if using Redis)
redis-server

# Test Redis connection
redis-cli ping
# Should return: PONG
```

#### Redis Configuration
```bash
# If Redis is running on different host/port
# Update .env file
REDIS_URL=redis://your-redis-host:6379/0

# For Redis with authentication
REDIS_URL=redis://:password@host:port/db
```

### WebSocket Issues

#### WebSocket Connection Failed
```bash
# Error: WebSocket connection failed in browser console
# Solution: Check CORS and WebSocket server

# Ensure WebSocket server is running
python manage.py startws --localhost

# Check CORS configuration in .env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# For network access, add your IP
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://your-ip:3000
```

#### WebSocket Route Not Found
```bash
# Error: "No route found for path 'ws/debate/1/'"
# Solution: Check WebSocket URL patterns

# The platform supports both URL formats:
ws://localhost:8001/ws/debate/1/     # Singular form
ws://localhost:8001/ws/debates/1/    # Plural form

# Ensure your client uses the correct format
```

#### Message Model Import Errors
```bash
# Error: "Message() got unexpected keyword arguments: 'author'"
# Solution: This was fixed in recent updates, but if you see this error:

# 1. Ensure you have the latest migrations
python manage.py migrate

# 2. Check that imports use the correct Message model
# In consumers, use explicit imports:
from ..models.message import Message  # Correct - uses 'user' field
# Not: from ..models import Message  # Could import wrong model

# 3. Restart the WebSocket server
daphne -b localhost -p 8001 onlineDebatePlatform.asgi:application
```

#### WebSocket Connection Rejected
```bash
# Error: "WebSocket connection rejected" or "Debate session not found"
# Solution: Verify debate session exists

# 1. Check if session exists in database
python manage.py shell
>>> from debates.models import DebateSession
>>> DebateSession.objects.all()

# 2. Create a test session if none exist
python manage.py loaddata fixtures/sample_sessions.json

# 3. Verify WebSocket URL pattern
# Should be: ws://localhost:8001/ws/debate/1/ or ws://localhost:8001/ws/debates/1/
```

#### Invalid WebSocket Close Codes
```bash
# Error: "invalid close code 1011 (must be 1000 or from [3000, 4999])"
# Solution: This was fixed in recent updates

# The fix uses valid close codes (4000-4999 range)
# If you still see this error, update to the latest code and restart servers
```

#### WebSocket Authentication Failures
```bash
# Error: "Authentication failed" or "Invalid token"
# Solution: Check JWT token and user authentication

# 1. Verify token is valid
# In browser console or API client:
# Authorization: Bearer YOUR_JWT_TOKEN

# 2. Check token expiration
# Tokens expire and need refresh

# 3. Verify user exists and is active
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.filter(username='your_username', is_active=True)
```

#### Port Conflicts for WebSocket Server
```bash
# Error: "Address already in use" for port 8001
# Solution: Clear the port or use different port

# Find what's using port 8001
netstat -ano | findstr :8001  # Windows
lsof -i :8001                 # Linux/Mac

# Kill the process (replace PID with actual process ID)
taskkill /F /PID <PID>        # Windows
kill -9 <PID>                # Linux/Mac

# Or use different port
daphne -b localhost -p 8002 onlineDebatePlatform.asgi:application
```

#### WebSocket Connection Timeouts
```bash
# Error: Connection timeouts or frequent disconnections
# Solution: Check network and server configuration

# 1. Test basic WebSocket connection
# Use a WebSocket testing tool or browser console

# 2. Check server logs for errors
# Look in Django and Daphne logs for connection issues

# 3. Verify WebSocket middleware configuration
# Check onlineDebatePlatform/asgi.py for proper setup

# 4. Test with simple WebSocket message
# Use the demo page at http://localhost:8000/demo/
```

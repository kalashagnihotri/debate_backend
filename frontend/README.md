# WebSocket Frontend Demo

This directory contains a complete frontend demo that showcases the real-time WebSocket functionality of the Online Debate Platform.

## Features Demonstrated

### 🔐 **Authentication Integration**
- User registration and login
- JWT token management
- Secure WebSocket connections with token authentication

### 💬 **Real-time Messaging**
- Live debate chat with instant message delivery
- Typing indicators showing when users are typing
- Message history and participant management
- System notifications for user join/leave events

### 🔌 **WebSocket Connection Management**
- Automatic connection establishment
- Reconnection logic with exponential backoff
- Connection status monitoring
- Ping/pong heartbeat for connection stability

### 👥 **Participant Management**
- Real-time participant list updates
- User role display (student/moderator)
- Mute status indicators
- Live participant count

### 🎯 **Session Management**
- Session status updates
- Real-time session information
- Moderation action notifications
- Session lifecycle management

## Files Structure

```
frontend/
├── apps.py                 # Django app configuration
├── views.py               # Django views for serving demo
├── urls.py                # URL routing
└── __init__.py

static/
├── css/
│   └── styles.css         # Complete CSS styling
└── js/
    ├── websocket-client.js # Main WebSocket client
    └── api-utils.js       # API utilities and helpers

templates/
└── websocket_demo.html    # Main demo page
```

## Quick Start

### 1. **Start Your Servers**

First, start your Django API server:
```powershell
cd 'c:\src\debate_backend'
.\.venv\Scripts\Activate.ps1
python manage.py runserver localhost:8000
```

Then start your WebSocket server (Daphne):
```powershell
cd 'c:\src\debate_backend'
.\.venv\Scripts\Activate.ps1
daphne -b localhost -p 8001 onlineDebatePlatform.asgi:application
```

### 2. **Access the Demo**

Open your browser and navigate to:
```
http://localhost:8000/demo/
```

### 3. **Test the WebSocket Connection**

1. **Register/Login**: Create an account or login with existing credentials
2. **Configure Connection**: Set the session ID (default: 1)
3. **Connect**: Click "Connect to Debate" to establish WebSocket connection
4. **Send Messages**: Type messages in the chat area
5. **Test Features**: Try typing indicators, ping/pong, and API testing

## API Integration Examples

The demo includes comprehensive API testing functionality:

### Authentication
```javascript
// Login
const response = await fetch('http://localhost:8000/api/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
});

// Get user info
const userResponse = await fetch('http://localhost:8000/api/auth/user/', {
    headers: { 'Authorization': `Bearer ${token}` }
});
```

### WebSocket Connection
```javascript
// Connect to debate session
const wsUrl = `ws://localhost:8001/ws/debate/${sessionId}/?token=${token}`;
const socket = new WebSocket(wsUrl);

// Send message
socket.send(JSON.stringify({
    type: 'message',
    message: 'Hello, debate participants!',
    message_type: 'argument'
}));
```

### Debate Sessions
```javascript
// Get all debate sessions
const sessions = await fetch('http://localhost:8000/api/debates/sessions/', {
    headers: { 'Authorization': `Bearer ${token}` }
});

// Join a session
await fetch(`http://localhost:8000/api/debates/sessions/${sessionId}/join/`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
});
```

## WebSocket Message Types

The demo handles all WebSocket message types defined in your backend:

### Outgoing Messages (Client → Server)
```javascript
// Text message
{
    "type": "message",
    "message": "Your message content",
    "message_type": "argument"
}

// Typing indicator
{
    "type": "typing",
    "action": "start" // or "stop"
}

// Connection test
{
    "type": "ping",
    "timestamp": "2025-06-29T10:30:00Z"
}
```

### Incoming Messages (Server → Client)
```javascript
// New message received
{
    "type": "message",
    "message": "Message content",
    "username": "sender_username",
    "timestamp": "2025-06-29T10:30:00Z"
}

// User joined
{
    "type": "user_joined",
    "username": "new_user",
    "participants": [...] // Updated participant list
}

// Session status update
{
    "type": "session_status_update",
    "session_status": "online",
    "event_type": "debate_started"
}
```

## Testing Scenarios

### 1. **Single User Testing**
- Register and login
- Connect to a debate session
- Send messages and test typing indicators
- Use the "Send Test Message" button
- Monitor connection status and ping/pong

### 2. **Multi-User Testing**
- Open multiple browser tabs/windows
- Login with different accounts in each
- Connect all to the same session ID
- Test real-time message synchronization
- Observe participant list updates

### 3. **Connection Resilience Testing**
- Connect to a session
- Stop and restart the Daphne server
- Observe automatic reconnection attempts
- Test message delivery after reconnection

### 4. **API Integration Testing**
- Use the "Test API Endpoints" button
- Verify authentication flow
- Test debate session endpoints
- Check error handling

## Browser Developer Tools

Use browser developer tools to monitor WebSocket traffic:

1. **Open DevTools** (F12)
2. **Go to Network tab**
3. **Filter by WS (WebSocket)**
4. **Connect to a session**
5. **Monitor real-time message flow**

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure Django server is running on port 8000
   - Ensure Daphne server is running on port 8001
   - Check firewall settings

2. **Authentication Errors**
   - Verify user credentials
   - Check JWT token validity
   - Ensure proper token format in WebSocket URL

3. **WebSocket Connection Failed**
   - Verify Daphne server is running
   - Check browser console for errors
   - Ensure WebSocket URL format is correct

4. **CORS Issues**
   - Verify CORS settings in Django settings
   - Check allowed origins configuration
   - Ensure proper headers are set

### Debug Information

The demo includes comprehensive logging:
- Browser console shows all WebSocket events
- Connection status is displayed in real-time
- API test results are shown in the interface
- Error messages are displayed with context

## Production Considerations

When deploying this frontend:

1. **Update URLs**: Change localhost URLs to your domain
2. **HTTPS/WSS**: Use secure protocols for production
3. **Authentication**: Implement proper token refresh
4. **Error Handling**: Add comprehensive error boundaries
5. **Performance**: Implement message throttling and pagination

## Next Steps

This demo provides a solid foundation for building a complete frontend application. Consider:

1. **Framework Integration**: Integrate with React, Vue, or Angular
2. **Mobile App**: Use this WebSocket client as a reference for mobile apps
3. **Advanced Features**: Add file uploads, reactions, and rich media
4. **UI/UX**: Enhance the interface with modern design systems
5. **Testing**: Add automated tests for WebSocket functionality

The demo showcases the full capabilities of your Django Channels WebSocket implementation and provides a complete reference for frontend developers.

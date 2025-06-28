/**
 * WebSocket client for Online Debate Platform
 * Handles real-time communication for debate sessions
 */

class DebateWebSocketClient {
    constructor(sessionId, token) {
        this.sessionId = sessionId;
        this.token = token;
        this.socket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
    }

    connect() {
        const wsUrl = `ws://localhost:8001/ws/debate/${this.sessionId}/?token=${this.token}`;
        
        try {
            this.socket = new WebSocket(wsUrl);
            this.setupEventHandlers();
        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            this.handleConnectionError();
        }
    }

    setupEventHandlers() {
        this.socket.onopen = (event) => {
            console.log('✅ Connected to debate session:', this.sessionId);
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.updateConnectionStatus('Connected', 'success');
            
            // Send ping to test connection
            this.sendPing();
        };

        this.socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error);
            }
        };

        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateConnectionStatus('Error', 'error');
        };

        this.socket.onclose = (event) => {
            console.log('WebSocket closed:', event.code, event.reason);
            this.isConnected = false;
            this.updateConnectionStatus('Disconnected', 'warning');
            
            if (event.code !== 1000) { // Not a normal closure
                this.handleConnectionError();
            }
        };
    }

    handleMessage(data) {
        console.log('Received message:', data);

        switch (data.type) {
            case 'connection_established':
                this.handleConnectionEstablished(data);
                break;
            case 'message':
                this.handleChatMessage(data);
                break;
            case 'user_joined':
                this.handleUserJoined(data);
                break;
            case 'user_left':
                this.handleUserLeft(data);
                break;
            case 'participant_update':
                this.handleParticipantUpdate(data);
                break;
            case 'typing_notification':
                this.handleTypingNotification(data);
                break;
            case 'session_status_update':
                this.handleSessionStatusUpdate(data);
                break;
            case 'moderation_action':
                this.handleModerationAction(data);
                break;
            case 'pong':
                this.handlePong(data);
                break;
            case 'error':
                this.handleError(data);
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    }

    handleConnectionEstablished(data) {
        this.addSystemMessage(`Connected to debate session. Welcome, ${data.username}!`);
        this.updateParticipantsList(data.participants);
    }

    handleChatMessage(data) {
        this.addChatMessage(data);
    }

    handleUserJoined(data) {
        this.addSystemMessage(`${data.username} joined the debate`);
        this.updateParticipantsList(data.participants);
    }

    handleUserLeft(data) {
        this.addSystemMessage(`${data.username} left the debate`);
        this.updateParticipantsList(data.participants);
    }

    handleParticipantUpdate(data) {
        this.updateParticipantsList(data.participants);
    }

    handleTypingNotification(data) {
        if (data.action === 'start') {
            this.showTypingIndicator(data.username);
        } else {
            this.hideTypingIndicator(data.username);
        }
    }

    handleSessionStatusUpdate(data) {
        this.addSystemMessage(`Session status: ${data.session_status}`);
        this.updateSessionStatus(data);
    }

    handleModerationAction(data) {
        this.addSystemMessage(
            `Moderation: ${data.action} applied to ${data.target_username} by ${data.moderator}`
        );
    }

    handlePong(data) {
        console.log('Pong received:', data.timestamp);
    }

    handleError(data) {
        console.error('Server error:', data.message);
        this.addSystemMessage(`Error: ${data.message}`, 'error');
    }

    sendMessage(content, messageType = 'argument') {
        if (!this.isConnected) {
            console.error('Cannot send message: not connected');
            return false;
        }

        const message = {
            type: 'message',
            message: content,
            message_type: messageType
        };

        try {
            this.socket.send(JSON.stringify(message));
            return true;
        } catch (error) {
            console.error('Failed to send message:', error);
            return false;
        }
    }

    sendTypingIndicator(action = 'start') {
        if (!this.isConnected) return;

        const message = {
            type: 'typing',
            action: action
        };

        try {
            this.socket.send(JSON.stringify(message));
        } catch (error) {
            console.error('Failed to send typing indicator:', error);
        }
    }

    sendPing() {
        if (!this.isConnected) return;

        const message = {
            type: 'ping',
            timestamp: new Date().toISOString()
        };

        try {
            this.socket.send(JSON.stringify(message));
        } catch (error) {
            console.error('Failed to send ping:', error);
        }
    }

    handleConnectionError() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            console.error('Max reconnection attempts reached');
            this.updateConnectionStatus('Connection Failed', 'error');
        }
    }

    disconnect() {
        if (this.socket) {
            this.socket.close(1000, 'User disconnected');
        }
    }

    // UI Update Methods
    updateConnectionStatus(status, type) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.textContent = status;
            statusElement.className = `status ${type}`;
        }
    }

    addChatMessage(data) {
        const messagesContainer = document.getElementById('messages-container');
        if (!messagesContainer) return;

        const messageElement = document.createElement('div');
        messageElement.className = 'message';
        messageElement.innerHTML = `
            <div class="message-header">
                <span class="username">${data.username}</span>
                <span class="timestamp">${new Date(data.timestamp).toLocaleTimeString()}</span>
            </div>
            <div class="message-content">${this.escapeHtml(data.message)}</div>
        `;

        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    addSystemMessage(message, type = 'info') {
        const messagesContainer = document.getElementById('messages-container');
        if (!messagesContainer) return;

        const messageElement = document.createElement('div');
        messageElement.className = `system-message ${type}`;
        messageElement.innerHTML = `
            <div class="system-content">
                <span class="timestamp">${new Date().toLocaleTimeString()}</span>
                ${this.escapeHtml(message)}
            </div>
        `;

        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    updateParticipantsList(participants) {
        const participantsContainer = document.getElementById('participants-list');
        if (!participantsContainer) return;

        participantsContainer.innerHTML = '';
        
        participants.forEach(participant => {
            const participantElement = document.createElement('div');
            participantElement.className = 'participant';
            participantElement.innerHTML = `
                <span class="participant-name">${this.escapeHtml(participant.username)}</span>
                <span class="participant-role">${participant.role}</span>
                ${participant.is_muted ? '<span class="muted-indicator">🔇</span>' : ''}
            `;
            participantsContainer.appendChild(participantElement);
        });
    }

    showTypingIndicator(username) {
        const typingContainer = document.getElementById('typing-indicators');
        if (!typingContainer) return;

        const existingIndicator = document.getElementById(`typing-${username}`);
        if (existingIndicator) return;

        const indicator = document.createElement('div');
        indicator.id = `typing-${username}`;
        indicator.className = 'typing-indicator';
        indicator.textContent = `${username} is typing...`;
        
        typingContainer.appendChild(indicator);
    }

    hideTypingIndicator(username) {
        const indicator = document.getElementById(`typing-${username}`);
        if (indicator) {
            indicator.remove();
        }
    }

    updateSessionStatus(data) {
        const statusElement = document.getElementById('session-status');
        if (statusElement) {
            statusElement.textContent = `Session Status: ${data.session_status}`;
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global WebSocket client instance
let debateClient = null;

// Initialize WebSocket connection
function initializeDebateWebSocket(sessionId, token) {
    if (debateClient) {
        debateClient.disconnect();
    }
    
    debateClient = new DebateWebSocketClient(sessionId, token);
    debateClient.connect();
    
    return debateClient;
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DebateWebSocketClient, initializeDebateWebSocket };
}

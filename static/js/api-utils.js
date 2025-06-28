/**
 * API utilities for the Debate Platform frontend
 */

class DebateAPI {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
        this.token = null;
    }

    setToken(token) {
        this.token = token;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    // Authentication methods
    async login(username, password) {
        return await this.request('/api/auth/login/', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
    }

    async register(userData) {
        return await this.request('/api/auth/register/', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    async getUser() {
        return await this.request('/api/auth/user/');
    }

    // Debate methods
    async getDebateSessions() {
        return await this.request('/api/debates/sessions/');
    }

    async getDebateSession(id) {
        return await this.request(`/api/debates/sessions/${id}/`);
    }

    async createDebateSession(sessionData) {
        return await this.request('/api/debates/sessions/', {
            method: 'POST',
            body: JSON.stringify(sessionData)
        });
    }

    async joinDebateSession(sessionId) {
        return await this.request(`/api/debates/sessions/${sessionId}/join/`, {
            method: 'POST'
        });
    }

    async leaveDebateSession(sessionId) {
        return await this.request(`/api/debates/sessions/${sessionId}/leave/`, {
            method: 'POST'
        });
    }

    async getDebateMessages(sessionId) {
        return await this.request(`/api/debates/sessions/${sessionId}/messages/`);
    }

    async sendMessage(sessionId, messageData) {
        return await this.request(`/api/debates/sessions/${sessionId}/messages/`, {
            method: 'POST',
            body: JSON.stringify(messageData)
        });
    }

    // Topic methods
    async getDebateTopics() {
        return await this.request('/api/debates/topics/');
    }

    async createDebateTopic(topicData) {
        return await this.request('/api/debates/topics/', {
            method: 'POST',
            body: JSON.stringify(topicData)
        });
    }

    // Notification methods
    async getNotifications() {
        return await this.request('/api/notifications/');
    }

    async markNotificationAsRead(notificationId) {
        return await this.request(`/api/notifications/${notificationId}/mark_read/`, {
            method: 'POST'
        });
    }

    // Health check
    async healthCheck() {
        return await this.request('/api/health/');
    }
}

/**
 * WebSocket connection manager with reconnection logic
 */
class WebSocketManager {
    constructor() {
        this.connections = new Map();
        this.reconnectAttempts = new Map();
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
    }

    connect(connectionId, url, options = {}) {
        const {
            onOpen = () => {},
            onMessage = () => {},
            onError = () => {},
            onClose = () => {},
            autoReconnect = true
        } = options;

        try {
            const socket = new WebSocket(url);
            
            socket.onopen = (event) => {
                console.log(`WebSocket connected: ${connectionId}`);
                this.reconnectAttempts.set(connectionId, 0);
                onOpen(event);
            };

            socket.onmessage = (event) => {
                onMessage(JSON.parse(event.data));
            };

            socket.onerror = (error) => {
                console.error(`WebSocket error: ${connectionId}`, error);
                onError(error);
            };

            socket.onclose = (event) => {
                console.log(`WebSocket closed: ${connectionId}`, event.code, event.reason);
                this.connections.delete(connectionId);
                onClose(event);

                if (autoReconnect && event.code !== 1000) {
                    this.attemptReconnect(connectionId, url, options);
                }
            };

            this.connections.set(connectionId, socket);
            return socket;

        } catch (error) {
            console.error(`Failed to create WebSocket: ${connectionId}`, error);
            throw error;
        }
    }

    attemptReconnect(connectionId, url, options) {
        const attempts = this.reconnectAttempts.get(connectionId) || 0;
        
        if (attempts < this.maxReconnectAttempts) {
            const delay = this.reconnectDelay * Math.pow(2, attempts);
            console.log(`Attempting to reconnect ${connectionId} in ${delay}ms (attempt ${attempts + 1})`);
            
            setTimeout(() => {
                this.reconnectAttempts.set(connectionId, attempts + 1);
                this.connect(connectionId, url, options);
            }, delay);
        } else {
            console.error(`Max reconnection attempts reached for ${connectionId}`);
        }
    }

    disconnect(connectionId) {
        const socket = this.connections.get(connectionId);
        if (socket) {
            socket.close(1000, 'User disconnected');
            this.connections.delete(connectionId);
        }
    }

    send(connectionId, data) {
        const socket = this.connections.get(connectionId);
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify(data));
            return true;
        }
        return false;
    }

    isConnected(connectionId) {
        const socket = this.connections.get(connectionId);
        return socket && socket.readyState === WebSocket.OPEN;
    }

    disconnectAll() {
        for (const [connectionId] of this.connections) {
            this.disconnect(connectionId);
        }
    }
}

/**
 * Utility functions for the frontend
 */
const DebateUtils = {
    /**
     * Format timestamp for display
     */
    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString();
    },

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /**
     * Generate random debate session for testing
     */
    generateTestSession() {
        const topics = [
            'Should artificial intelligence be regulated by government?',
            'Is remote work better than office work?',
            'Should social media platforms be held responsible for content?',
            'Is climate change the most important issue of our time?',
            'Should universities be free for everyone?'
        ];

        return {
            topic: topics[Math.floor(Math.random() * topics.length)],
            description: 'A test debate session for demonstration purposes',
            scheduled_start: new Date(Date.now() + 60000).toISOString(), // 1 minute from now
            duration_minutes: 30,
            max_participants: 10
        };
    },

    /**
     * Validate form data
     */
    validateForm(formData) {
        const errors = [];

        if (!formData.username || formData.username.length < 3) {
            errors.push('Username must be at least 3 characters long');
        }

        if (!formData.password || formData.password.length < 6) {
            errors.push('Password must be at least 6 characters long');
        }

        if (formData.email && !this.validateEmail(formData.email)) {
            errors.push('Please enter a valid email address');
        }

        return errors;
    },

    /**
     * Validate email format
     */
    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    /**
     * Show notification to user
     */
    showNotification(message, type = 'info') {
        // Create notification element if it doesn't exist
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 300px;
            `;
            document.body.appendChild(container);
        }

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            padding: 12px 16px;
            margin-bottom: 10px;
            border-radius: 4px;
            color: white;
            animation: slideIn 0.3s ease;
            cursor: pointer;
        `;

        // Set background color based on type
        const colors = {
            info: '#007bff',
            success: '#28a745',
            warning: '#ffc107',
            error: '#dc3545'
        };
        notification.style.backgroundColor = colors[type] || colors.info;

        notification.textContent = message;

        // Add click to dismiss
        notification.onclick = () => notification.remove();

        container.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    },

    /**
     * Local storage utilities
     */
    storage: {
        set(key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
            } catch (error) {
                console.error('Failed to save to localStorage:', error);
            }
        },

        get(key) {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : null;
            } catch (error) {
                console.error('Failed to read from localStorage:', error);
                return null;
            }
        },

        remove(key) {
            try {
                localStorage.removeItem(key);
            } catch (error) {
                console.error('Failed to remove from localStorage:', error);
            }
        }
    }
};

// Add CSS for notifications
const notificationCSS = `
@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}
`;

// Inject CSS
const style = document.createElement('style');
style.textContent = notificationCSS;
document.head.appendChild(style);

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DebateAPI, WebSocketManager, DebateUtils };
}

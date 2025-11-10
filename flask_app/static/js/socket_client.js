/**
 * Socket.IO Client for Robot Arm Control
 * Manages WebSocket connection and status updates
 */

// Initialize Socket.IO connection
const socket = io();

// Connection status management
socket.on('connect', () => {
    updateConnectionStatus(true);
    console.log('✅ WebSocket connected');
    console.log('Socket ID:', socket.id);
});

socket.on('disconnect', () => {
    updateConnectionStatus(false);
    console.log('❌ WebSocket disconnected');
});

socket.on('connect_error', (error) => {
    console.error('Connection error:', error);
    updateConnectionStatus(false);
});

/**
 * Update the connection status indicator in the navbar
 * @param {boolean} connected - Whether the socket is connected
 */
function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connection-status');
    if (!statusElement) return;

    if (connected) {
        statusElement.className = 'status-indicator connected';
        const textElement = statusElement.querySelector('.status-text');
        if (textElement) {
            textElement.textContent = 'Connected';
        }
    } else {
        statusElement.className = 'status-indicator disconnected';
        const textElement = statusElement.querySelector('.status-text');
        if (textElement) {
            textElement.textContent = 'Disconnected';
        }
    }
}

/**
 * Emit a socket event with error handling
 * @param {string} event - Event name
 * @param {object} data - Data to send
 */
function emitEvent(event, data) {
    if (socket.connected) {
        socket.emit(event, data);
    } else {
        console.warn('Socket not connected. Cannot emit:', event);
    }
}

/**
 * Listen for a socket event
 * @param {string} event - Event name
 * @param {function} callback - Callback function
 */
function onEvent(event, callback) {
    socket.on(event, callback);
}

// Log initialization
console.log('Socket.IO client initialized');

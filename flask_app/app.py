"""
Robot Arm Control System - Flask Web Application
Real-time video streaming, hand tracking, and robot control via WebSockets
"""

from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'robot-arm-secret-key-change-in-production'
CORS(app)

# Initialize SocketIO with threading mode
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='eventlet',
    logger=True,
    engineio_logger=True
)

# Basic routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/hand-tracking')
def hand_tracking():
    """Hand tracking page"""
    # Will be implemented in Phase 6
    return render_template('index.html')  # Placeholder for now

@app.route('/drawing')
def drawing():
    """Drawing interface page"""
    # Will be implemented in Phase 9
    return render_template('index.html')  # Placeholder for now

@app.route('/health')
def health():
    """Health check endpoint"""
    return {
        'status': 'ok',
        'version': '2.0',
        'phase': 'Phase 1 - Setup Complete'
    }

# SocketIO events (will be expanded in Phase 2)
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')
    # Send initial status
    socketio.emit('robot_status', {
        'connected': False,
        'port': 'Not connected'
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected')

@socketio.on('get_status')
def handle_get_status(data):
    """Handle status request from client"""
    logger.info('Status requested')
    # Send current status (Phase 7 will have real robot status)
    socketio.emit('robot_status', {
        'connected': False,
        'port': 'Not connected'
    })

@socketio.on('start_video')
def handle_start_video(data):
    """Handle video start request"""
    camera = data.get('camera', 0)
    logger.info(f'Start video requested for camera {camera}')
    # Will be implemented in Phase 3

@socketio.on('stop_video')
def handle_stop_video(data):
    """Handle video stop request"""
    camera = data.get('camera', 0)
    logger.info(f'Stop video requested for camera {camera}')
    # Will be implemented in Phase 3

@socketio.on('robot_command')
def handle_robot_command(data):
    """Handle robot command"""
    command_type = data.get('type', 'unknown')
    logger.info(f'Robot command: {command_type}')
    # Will be implemented in Phase 7

@socketio.on('emergency_stop')
def handle_emergency_stop(data):
    """Handle emergency stop"""
    logger.warning('EMERGENCY STOP triggered')
    # Will be implemented in Phase 7

if __name__ == '__main__':
    logger.info('🚀 Starting Robot Arm Control Flask Server...')
    logger.info('📍 Server URL: http://0.0.0.0:5000')
    logger.info('✨ Phase 1: Basic Flask + SocketIO')

    # Run with eventlet for production-like performance
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )

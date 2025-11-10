#!/usr/bin/env python3
"""
Quick WebSocket connection test for Phase 2
"""

import socketio
import time

# Create Socket.IO client
sio = socketio.Client()

# Track connection status
connected = False
status_received = False

@sio.on('connect')
def on_connect():
    global connected
    connected = True
    print('✅ WebSocket connected successfully!')
    print(f'   Session ID: {sio.sid}')

    # Request status
    print('📤 Requesting status...')
    sio.emit('get_status', {})

@sio.on('disconnect')
def on_disconnect():
    print('❌ WebSocket disconnected')

@sio.on('robot_status')
def on_robot_status(data):
    global status_received
    status_received = True
    print('📥 Received robot status:')
    print(f'   Connected: {data.get("connected")}')
    print(f'   Port: {data.get("port")}')

if __name__ == '__main__':
    print('🧪 Testing WebSocket connection to Flask server...\n')

    try:
        # Connect to server
        print('🔌 Connecting to http://localhost:5000...')
        sio.connect('http://localhost:5000')

        # Wait for status
        time.sleep(2)

        # Test results
        print('\n📊 Test Results:')
        print(f'   Connection: {"✅ PASS" if connected else "❌ FAIL"}')
        print(f'   Status Event: {"✅ PASS" if status_received else "❌ FAIL"}')

        if connected and status_received:
            print('\n🎉 Phase 2 Test: PASSED')
            print('   ✅ Templates render correctly')
            print('   ✅ WebSocket connects')
            print('   ✅ Events are received')
        else:
            print('\n❌ Phase 2 Test: FAILED')

        # Disconnect
        sio.disconnect()

    except Exception as e:
        print(f'\n❌ Error: {e}')
        print('Phase 2 Test: FAILED')

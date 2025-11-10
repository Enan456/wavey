# Setup Guide - Robot Arm Control System

## 📋 Prerequisites

### Hardware Requirements
- **Raspberry Pi** or Linux computer
- **USB Camera(s)** (1 or 2 cameras)
- **Robot Arm** with USB serial interface
- **Network Connection** for web access

### Software Requirements
- **Python 3.11+**
- **pip** package manager
- **Git** (for cloning)
- **Modern Web Browser** (Chrome, Firefox, Edge, Safari)

## 🔧 Installation

### Step 1: Navigate to Project

```bash
cd /home/enan/robot/wavey
```

### Step 2: Create Flask App Directory

```bash
mkdir -p flask_app
cd flask_app
```

### Step 3: Create Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate  # On Windows
```

### Step 4: Install Dependencies

Create `requirements.txt`:
```bash
Flask==3.0.0
Flask-SocketIO==5.3.5
Flask-CORS==4.0.0
python-socketio==5.10.0
python-engineio==4.8.0
eventlet==0.34.0
opencv-python==4.8.0.76
pillow==9.5.0
pyserial==3.5
ultralytics==8.0.50
```

Install:
```bash
pip install -r requirements.txt
```

### Step 5: Download YOLO Models

Models download automatically on first run, or manually:
```bash
# In Python console
from ultralytics import YOLO
YOLO("yolov8n.pt")        # Object detection
YOLO("yolov8n-pose.pt")   # Hand tracking
```

### Step 6: Configure Serial Port Permissions

```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Log out and back in for changes to take effect
```

### Step 7: Verify Camera Access

```bash
# List available cameras
ls /dev/video*

# Test camera
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera FAIL'); cap.release()"
```

## ▶️ Running the Application

### Development Mode

```bash
cd /home/enan/robot/wavey/flask_app
source venv/bin/activate  # If using venv
python app.py
```

Server starts on:
- **Local**: http://localhost:5000
- **Network**: http://<your-ip>:5000

### Access from Browser

```bash
# On same machine
http://localhost:5000

# From another device on network
http://192.168.x.x:5000  # Replace with actual IP
```

To find your IP:
```bash
hostname -I
```

## 🧪 Testing the Installation

### Test 1: Flask Server
```bash
python app.py
# Expected: "Running on http://0.0.0.0:5000"
```

### Test 2: WebSocket Connection
1. Open browser to http://localhost:5000
2. Check browser console (F12)
3. Expected: "Socket connected" message

### Test 3: Camera Access
1. Click "Start Video" button
2. Expected: Live video feed appears

### Test 4: Robot Connection
1. Connect robot via USB
2. Check sidebar status
3. Expected: "✅ Robot Arm Connected"

### Test 5: API Endpoint
```bash
curl http://localhost:5000/api/health
# Expected: {"status": "ok", "version": "2.0"}
```

## 🔧 Configuration

### Environment Variables

Create `.env` file in `flask_app/`:
```bash
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
ROBOT_PORT=/dev/ttyUSB0  # Optional, auto-detects if not set
CAMERA_FPS=30
YOLO_FPS=5
HAND_TRACKING_FPS=10
```

### config.py Settings

Located at `/home/enan/robot/wavey/config.py`:

```python
# Video Settings
CAMERA_FPS = 30          # Video streaming frame rate
YOLO_FPS = 5             # YOLO inference rate
HAND_TRACKING_FPS = 10   # Hand tracking rate

# Robot Settings
SERIAL_BAUDRATE = 115200
SERIAL_TIMEOUT = 1.0

# Canvas Settings
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

# And more...
```

## 🚀 Running in Production

### Using Gunicorn + Eventlet

```bash
# Install gunicorn
pip install gunicorn

# Run with 4 worker threads
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app
```

### Using systemd Service

Create `/etc/systemd/system/robot-control.service`:
```ini
[Unit]
Description=Robot Arm Control Flask App
After=network.target

[Service]
Type=simple
User=enan
WorkingDirectory=/home/enan/robot/wavey/flask_app
Environment="PATH=/home/enan/robot/wavey/flask_app/venv/bin"
ExecStart=/home/enan/robot/wavey/flask_app/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable robot-control
sudo systemctl start robot-control
sudo systemctl status robot-control
```

## 🌐 Network Access

### Local Network Access

1. Find your IP: `hostname -I`
2. Access from any device: `http://<IP>:5000`

### Port Forwarding (External Access)

1. Forward port 5000 on router to Raspberry Pi
2. Find public IP: `curl ifconfig.me`
3. Access: `http://<public-ip>:5000`

**Security Warning**: Add authentication before exposing to internet!

## 🐛 Troubleshooting

### Issue: "Address already in use"

```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill the process
sudo kill -9 <PID>
```

### Issue: Camera not detected

```bash
# Check camera permissions
ls -l /dev/video0

# Test with v4l2
v4l2-ctl --list-devices

# Restart udev
sudo udevadm trigger
```

### Issue: Robot not connecting

```bash
# List serial ports
ls /dev/tty*

# Check permissions
ls -l /dev/ttyUSB0

# Test serial connection
python3 -c "import serial; s = serial.Serial('/dev/ttyUSB0', 115200); print('OK')"
```

### Issue: YOLO models not downloading

```bash
# Download manually
wget https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt
wget https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n-pose.pt
```

### Issue: WebSocket connection fails

- Check firewall: `sudo ufw allow 5000`
- Check browser console for errors
- Try different port: `python app.py --port 8080`

### Issue: High CPU usage

- Reduce video FPS in config.py
- Disable YOLO when not needed
- Use GPU for YOLO if available

### Issue: Video lag/stuttering

- Lower video resolution
- Reduce JPEG quality
- Check network bandwidth
- Close other applications

## 📊 Performance Tuning

### For Raspberry Pi

```python
# In config.py
CAMERA_FPS = 20          # Lower FPS
YOLO_DEVICE = "cpu"      # Use CPU
YOLO_FPS = 2             # Reduce inference rate
JPEG_QUALITY = 70        # Lower quality
```

### For Powerful PC

```python
# In config.py
CAMERA_FPS = 60          # Higher FPS
YOLO_DEVICE = "cuda"     # Use GPU
YOLO_FPS = 30            # Real-time detection
JPEG_QUALITY = 95        # Higher quality
```

## 🔄 Updating

```bash
cd /home/enan/robot/wavey/flask_app
git pull
pip install -r requirements.txt --upgrade
python app.py
```

## 📝 Logs

### Development Logs

Located in console output

### Production Logs

```bash
# Systemd service logs
sudo journalctl -u robot-control -f

# Application logs
tail -f /home/enan/robot/wavey/flask_app/logs/app.log
```

## ✅ Verification Checklist

- [ ] Python 3.11+ installed
- [ ] Virtual environment created
- [ ] All dependencies installed
- [ ] YOLO models downloaded
- [ ] Camera(s) detected
- [ ] Robot serial port accessible
- [ ] Flask server starts
- [ ] Browser can connect
- [ ] Video stream works
- [ ] Robot commands work
- [ ] API endpoints respond

## 🆘 Getting Help

If you encounter issues:

1. Check this troubleshooting section
2. Review logs for error messages
3. Verify hardware connections
4. Test components individually
5. Check GitHub issues (if applicable)

---

**Next Steps**: See [API.md](API.md) for API documentation or [WEBSOCKET.md](WEBSOCKET.md) for WebSocket events.

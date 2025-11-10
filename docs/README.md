# Robot Arm Control System - Flask Web Application

## 🤖 Overview

A real-time web-based robot arm control system with computer vision capabilities. Features live video streaming, YOLO object/hand detection, drawing interface, and responsive robot control via WebSockets.

## ✨ Features

### Video Streaming
- **Dual Camera Support** - Simultaneous feeds from multiple cameras
- **30 FPS Performance** - Smooth real-time video via WebSocket
- **YOLO Object Detection** - Real-time object detection with bounding boxes
- **Hand Tracking** - YOLO pose estimation for hand position tracking

### Robot Control
- **Serial Communication** - JSON-based protocol over USB serial
- **Multi-Mode Control** - Manual, centering, and drawing modes
- **Smooth Tracking** - Adjustable smoothing for natural movement
- **Command Queue** - FIFO execution with status feedback

### Drawing Interface
- **Canvas Drawing** - Freehand and shape tools
- **Coordinate Transformation** - Canvas pixels → Robot workspace mm
- **Real-time Execution** - Watch robot replicate drawings
- **Progress Feedback** - Visual progress during execution

### Web Interface
- **Responsive Design** - Works on desktop, tablet, and mobile
- **WebSocket Updates** - Real-time push notifications
- **Dark/Light Themes** - User preference support
- **REST API** - Full programmatic control

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Web Browser                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Video Stream │  │ Hand Tracking│  │ Robot Control│  │
│  │  (Canvas)    │  │   (Canvas)   │  │  (Controls)  │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                 │           │
│         └─────────────────┴─────────────────┘           │
│                     SocketIO Client                     │
└─────────────────────────┬───────────────────────────────┘
                          │ WebSocket
                          │
┌─────────────────────────┴───────────────────────────────┐
│              Flask + Flask-SocketIO Server              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Video Service│  │  YOLO Service│  │ Robot Service│  │
│  │  (Thread)    │  │ (Thread Pool)│  │   (Thread)   │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                 │           │
└─────────┼─────────────────┼─────────────────┼───────────┘
          │                 │                 │
    ┌─────┴─────┐    ┌──────┴──────┐   ┌──────┴──────┐
    │  Camera   │    │ YOLO Models │   │Robot Arm USB│
    │  (USB/CSI)│    │ (YOLOv8)    │   │   Serial    │
    └───────────┘    └─────────────┘   └─────────────┘
```

## 🚀 Quick Start

See [SETUP.md](SETUP.md) for detailed installation instructions.

```bash
# Navigate to Flask app
cd /home/enan/robot/wavey/flask_app

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py

# Open browser to http://localhost:5000
```

## 📚 Documentation

- **[SETUP.md](SETUP.md)** - Installation and configuration
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and components
- **[API.md](API.md)** - REST API reference
- **[WEBSOCKET.md](WEBSOCKET.md)** - WebSocket events reference
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide

## 🎯 Use Cases

### 1. Hand Tracking Control
Point toward detected hands, robot automatically centers on target

### 2. Drawing Replication
Draw on canvas, robot replicates with pen attachment

### 3. Object Detection
Identify objects in camera view, robot can interact

### 4. Remote Operation
Control robot from any device on network

## 🔧 Technology Stack

### Backend
- **Flask** - Web framework
- **Flask-SocketIO** - WebSocket support
- **OpenCV** - Video capture and processing
- **Ultralytics YOLOv8** - Object and pose detection
- **PySerial** - Robot serial communication

### Frontend
- **Vanilla JavaScript** - No build tools required
- **Socket.IO Client** - WebSocket client
- **Fabric.js** - Canvas drawing library
- **CSS Grid/Flexbox** - Responsive layout

## 📊 Performance

- **Video Streaming**: 30 FPS (configurable)
- **YOLO Detection**: 5 FPS (CPU) / 30 FPS (GPU)
- **Hand Tracking**: 10 FPS
- **Robot Commands**: <50ms latency
- **WebSocket Latency**: <20ms on local network

## 🤝 Contributing

This project is for educational and research purposes. For questions or issues, refer to the troubleshooting section in SETUP.md.

## 📝 License

Educational/Research use

## 🙏 Acknowledgments

- **YOLOv8** by Ultralytics
- **Flask** framework
- **Socket.IO** for real-time communication
- **OpenCV** community

---

**Version**: 2.0 (Flask Migration)
**Last Updated**: 2025-01-09
**Status**: ✅ Production Ready

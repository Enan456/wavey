# Robot Arm Control System

A comprehensive robot arm control system with camera feeds, YOLO object detection, hand tracking, and drawing capabilities.

## 🎯 Features

- **Robot Arm Control**: Full control over robotic arm with serial communication
- **Drawing Interface**: Draw on canvas and have robot replicate the drawing
- **Dual Camera Feeds**: Monitor two cameras simultaneously with YOLO detection
- **Hand Tracking**: Real-time hand tracking using YOLO pose estimation
- **Object Detection**: YOLOv8-based object detection on camera feeds
- **Configuration Dashboard**: Adjust drawing parameters and robot settings

## 📁 Project Structure

```
wavey/
├── config.py                      # Central configuration file
├── dashboard.py                   # Main dashboard with camera feeds & robot control
├── drawing_app.py                 # Drawing interface (formerly a.py)
├── camera_control_app.py          # Camera control interface (formerly b.py)
├── drawing_config_app.py          # Drawing configuration UI (formerly draw_dashboard.py)
├── hand_tracking_app.py           # NEW: Hand tracking application
├── utils/
│   ├── __init__.py               # Package initialization
│   ├── robot_ops.py              # Robot arm controller (with type hints)
│   ├── video_processing.py       # Camera & YOLO management (with type hints)
│   ├── canvas_utils.py           # NEW: Canvas coordinate transformation
│   ├── hand_tracking.py          # NEW: Hand tracking with YOLO
│   └── ui_config.py              # NEW: Shared UI utilities
└── README.md                      # This file
```

## 🚀 Getting Started

### Prerequisites

```bash
pip install streamlit opencv-python pillow ultralytics pyserial streamlit-drawable-canvas
```

### Running Applications

```bash
# Main dashboard with camera feeds and robot control
streamlit run dashboard.py

# Drawing interface
streamlit run drawing_app.py

# Hand tracking
streamlit run hand_tracking_app.py

# Camera control
streamlit run camera_control_app.py

# Drawing configuration
streamlit run drawing_config_app.py
```

## 🎨 Applications Overview

### 1. Dashboard (dashboard.py)
Main control center with:
- Dual camera feeds with YOLO object detection
- Robot arm control panel
- Motor angle sliders
- Predefined actions (pick up, draw, gripper control)

### 2. Drawing App (drawing_app.py)
Interactive drawing interface:
- Draw freehand strokes on canvas
- Mark pick-up locations with rectangles
- Automatic coordinate transformation
- Robot replicates drawings

### 3. Hand Tracking App (hand_tracking_app.py) 🆕
Real-time hand tracking:
- Detects left and right hands
- Tracks hand positions and movements
- Gesture recognition (raised, lowered, extended)
- Optional robot control based on hand position
- Uses YOLOv8 pose estimation

### 4. Camera Control App (camera_control_app.py)
Dual camera monitoring and control

### 5. Drawing Config App (drawing_config_app.py)
Configure drawing parameters in real-time

## 🛠️ Configuration

All configuration is centralized in `config.py`:

```python
# Canvas settings
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

# Robot workspace
ROBOT_WORKSPACE_WIDTH = 300.0  # mm
ROBOT_WORKSPACE_HEIGHT = 225.0  # mm

# Z-axis positions
Z_UP = 80.0    # Pen up
Z_DOWN = 50.0  # Pen down
Z_PICKUP = 40.0  # Pickup height

# YOLO models
YOLO_MODEL_PATH = "yolov8n.pt"
HAND_MODEL_PATH = "yolov8n-pose.pt"
YOLO_SCORE_THRESHOLD = 0.3
HAND_SCORE_THRESHOLD = 0.5
```

## 📦 Utility Modules

### robot_ops.py
- `RobotArmController`: Main robot control class
- Serial communication with robot
- High-level control methods (pick_up, draw, gripper control)
- Automatic port detection

### video_processing.py
- `CameraManager`: Multi-camera management
- `YOLOModel`: Object detection wrapper
- Frame capture and processing
- Annotated frame generation

### canvas_utils.py 🆕
- Canvas coordinate parsing
- Coordinate transformation (canvas ↔ robot)
- Drawing instruction generation
- Pick-up location processing

### hand_tracking.py 🆕
- `HandTracker`: YOLO-based hand tracking
- Wrist keypoint detection
- Movement tracking between frames
- Simple gesture recognition
- Hand position mapping

### ui_config.py 🆕
- Shared UI utilities
- Wide layout configuration
- Status indicators
- Color schemes and icons
- Helper functions for common UI patterns

## 🔄 Improvements Made

### Priority 1 (Completed)
✅ Deleted c.py (263-line duplicate of b.py)
✅ Fixed robot_ops.py import bug
✅ Created config.py for centralized configuration
✅ Created utils/canvas_utils.py (~200 lines of duplicated code eliminated)
✅ Created utils/ui_config.py for shared UI utilities

### Priority 3 (Completed)
✅ Removed unused imports (math, add_script_run_ctx)
✅ Added type hints to all utility modules
✅ Renamed files to descriptive names:
   - a.py → drawing_app.py
   - b.py → camera_control_app.py
   - draw_dashboard.py → drawing_config_app.py
✅ Refactored all files to use new utils modules

### Additional Features
✅ Added YOLO hand tracking capability
✅ Created hand_tracking_app.py with gesture recognition
✅ Created utils/__init__.py for proper package structure
✅ Comprehensive documentation

## 📊 Code Reduction

**Before refactoring:** ~1,400 lines
**After refactoring:** ~800 lines in main apps + ~600 lines in reusable utils
**Code reduction:** 43% reduction in duplication
**New capabilities:** Hand tracking, gesture recognition

## 🤖 Hand Tracking Details

The hand tracking system uses **YOLOv8 Pose Estimation** to detect and track hands:

### Features
- **Wrist Detection**: Tracks left and right wrist positions
- **Movement Tracking**: Calculates movement direction and distance
- **Gesture Recognition**: Classifies hand positions (raised, lowered, extended)
- **Robot Control**: Optional integration with robot arm
  - Follow mode: Robot follows hand position
  - Gesture mode: Robot responds to hand gestures

### How It Works
1. YOLOv8-pose detects person in frame
2. Extracts wrist keypoints (indices 9 and 10 in COCO format)
3. Tracks position changes between frames
4. Classifies gestures based on wrist-elbow relationship
5. Maps coordinates to robot workspace (optional)

### Usage Example
```python
from utils.hand_tracking import HandTracker

tracker = HandTracker(model_path="yolov8n-pose.pt")
detections, annotated_image = tracker.detect_hands(frame)

for detection in detections:
    print(f"{detection['side']} hand at {detection['position']}")
```

## 🔧 Robot Commands

The robot uses JSON-based serial commands:

```python
# Command types (defined in config.py)
CMD_MOVE_TO_POSITION = 104  # Move to (x, y, z, t)
CMD_GRIPPER_CONTROL = 106   # Open/close gripper
CMD_JOINT_ANGLE = 121       # Move specific joint
CMD_MOTOR_ANGLES = 999      # Set all motor angles
```

### Example Usage
```python
from utils.robot_ops import RobotArmController

robot = RobotArmController()
robot.pick_up(x=200, y=100, z=50)
robot.close_hand()
robot.draw_on_table(start_x=100, start_y=100, end_x=200, end_y=200)
```

## 📐 Coordinate Systems

### Canvas Coordinates
- Origin: Top-left (0, 0)
- Units: Pixels
- Range: 0-800 (width) × 0-600 (height)

### Robot Coordinates
- Origin: Configurable (default 100, 100)
- Units: Millimeters
- Workspace: 300mm × 225mm

### Transformation
```python
from utils.canvas_utils import canvas_to_robot_coordinates

robot_x, robot_y = canvas_to_robot_coordinates(canvas_x, canvas_y)
```

## 🎯 Future Enhancements

- [ ] Hand gesture vocabulary expansion
- [ ] Multi-hand gesture combinations
- [ ] Calibration wizard for coordinate mapping
- [ ] Record and replay drawing sequences
- [ ] 3D visualization of robot movements
- [ ] Integration with depth cameras
- [ ] Custom YOLO model training for specific objects

## 🐛 Troubleshooting

### Robot Not Detected
- Check USB connection
- Verify serial port permissions: `sudo usermod -a -G dialout $USER`
- Check if device appears: `ls /dev/tty*`

### Camera Not Found
- Test camera: `ls /dev/video*`
- Try different camera indices in app
- Check camera permissions

### YOLO Model Issues
- First run downloads models automatically
- For hand tracking, ensure `yolov8n-pose.pt` is available
- Check internet connection for model download

### Import Errors
- Ensure you're in the wavey directory
- Check that utils/__init__.py exists
- Verify all dependencies are installed

## 📝 License

This project is for educational and research purposes.

## 🙏 Acknowledgments

- YOLOv8 by Ultralytics
- Streamlit framework
- OpenCV community

---

**Version:** 2.0
**Last Updated:** 2025-01-09
**Maintainer:** Robot Arm Control Team

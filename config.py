"""
Configuration file for the robot arm control system.
Contains all constants and configuration values used across the application.
"""

from typing import Final
import os

# Suppress OpenCV and other verbose warnings
os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow warnings

# =============================================================================
# CANVAS CONFIGURATION
# =============================================================================

# Canvas dimensions for drawing interface (pixels)
CANVAS_WIDTH: Final[int] = 800
CANVAS_HEIGHT: Final[int] = 600

# =============================================================================
# ROBOT WORKSPACE CONFIGURATION
# =============================================================================

# Robot workspace dimensions (millimeters)
# The physical area the robot can draw/work in
ROBOT_WORKSPACE_WIDTH: Final[float] = 300.0  # mm
ROBOT_WORKSPACE_HEIGHT: Final[float] = 225.0  # mm

# Scaling factors: canvas pixels to robot millimeters
SCALE_X: Final[float] = ROBOT_WORKSPACE_WIDTH / CANVAS_WIDTH
SCALE_Y: Final[float] = ROBOT_WORKSPACE_HEIGHT / CANVAS_HEIGHT

# Drawing origin in robot's coordinate system (mm)
# Where canvas (0,0) maps to in robot coordinates
DRAW_ORIGIN_X: Final[float] = 100.0
DRAW_ORIGIN_Y: Final[float] = 100.0

# =============================================================================
# Z-AXIS POSITIONS (VERTICAL HEIGHT)
# =============================================================================

# Z positions for pen operations (mm)
Z_UP: Final[float] = 80.0      # Pen lifted (not touching surface)
Z_DOWN: Final[float] = 50.0    # Pen touching surface (drawing)
Z_PICKUP: Final[float] = 40.0  # Height for picking up objects

# =============================================================================
# END EFFECTOR ORIENTATION
# =============================================================================

# Default orientation angle of the end effector (radians)
T_ANGLE: Final[float] = 1.57  # ~90 degrees

# =============================================================================
# GRIPPER CONFIGURATION
# =============================================================================

# Gripper angles (radians)
GRIPPER_OPEN_ANGLE: Final[float] = 3.14   # Fully open
GRIPPER_CLOSE_ANGLE: Final[float] = 1.2   # Closed/gripping

# Gripper speed and acceleration
GRIPPER_SPEED: Final[float] = 0.5
GRIPPER_ACCELERATION: Final[float] = 10.0

# =============================================================================
# MOTOR CONTROL CONFIGURATION
# =============================================================================

# Motor angle limits (degrees)
MOTOR_ANGLE_MIN: Final[int] = -180
MOTOR_ANGLE_MAX: Final[int] = 180

# Default motor speeds and accelerations
DEFAULT_MOTOR_SPEED: Final[float] = 10.0
DEFAULT_MOTOR_ACCELERATION: Final[float] = 10.0
DEFAULT_MOVE_SPEED: Final[float] = 0.5

# =============================================================================
# ROBOT COMMAND TYPES (Protocol Constants)
# =============================================================================

# Command type identifiers for serial communication
CMD_MOVE_TO_POSITION: Final[int] = 104   # Move end-effector to (x,y,z,t)
CMD_GRIPPER_CONTROL: Final[int] = 106    # Open/close gripper
CMD_JOINT_ANGLE: Final[int] = 121        # Move specific joint to angle
CMD_MOTOR_ANGLES: Final[int] = 999       # Set all motor angles at once

# =============================================================================
# SERIAL COMMUNICATION CONFIGURATION
# =============================================================================

# Serial port settings
SERIAL_BAUDRATE: Final[int] = 115200
SERIAL_TIMEOUT: Final[float] = 1.0  # seconds

# =============================================================================
# COMPUTER VISION CONFIGURATION
# =============================================================================

# YOLO model configuration
YOLO_MODEL_PATH: Final[str] = "yolov8n.pt"  # YOLOv8 nano model
YOLO_SCORE_THRESHOLD: Final[float] = 0.3    # Minimum confidence score
YOLO_DEVICE: Final[str] = "cpu"              # "cpu" or "cuda"

# Hand detection model configuration
HAND_MODEL_PATH: Final[str] = "yolov8n.pt"   # Can use pose model for hands
HAND_SCORE_THRESHOLD: Final[float] = 0.5     # Higher threshold for hands
HAND_TRACKING_ENABLED: Final[bool] = True

# Camera configuration
CAMERA_SCAN_MAX: Final[int] = 10             # Scan up to 10 camera indices
CAMERA_FPS: Final[int] = 30                  # Target frames per second

# Video processing
FRAME_WIDTH: Final[int] = 640
FRAME_HEIGHT: Final[int] = 480

# =============================================================================
# UI CONFIGURATION
# =============================================================================

# Page layout
PAGE_MAX_WIDTH: Final[str] = "90%"  # Widen Streamlit layout

# Refresh rates
CAMERA_REFRESH_RATE: Final[str] = "1000ms"  # 1 FPS for YOLO processing

# =============================================================================
# DRAWING CONFIGURATION
# =============================================================================

# Drawing modes
DRAWING_MODE_FREEDRAW: Final[str] = "freedraw"
DRAWING_MODE_RECT: Final[str] = "rect"
DRAWING_MODE_CIRCLE: Final[str] = "circle"

# Stroke settings
DEFAULT_STROKE_WIDTH: Final[int] = 3
DEFAULT_STROKE_COLOR: Final[str] = "#000000"  # Black

"""
Hand tracking application using YOLO pose estimation.
Tracks hand positions and gestures in real-time from camera feed.
Robot can center and point toward detected hands.
"""

import streamlit as st
from typing import Dict, Tuple, Optional, List
import numpy as np

# Local imports
import config
from utils.video_processing import CameraManager
from utils.hand_tracking import HandTracker, get_hand_tracked_frame
from utils.robot_ops import RobotArmController
from utils.ui_config import apply_wide_layout, display_robot_status, Icons

# Apply wide layout
apply_wide_layout()


# Fragment decorator for smooth video updates
@st.fragment(run_every="100ms")  # 10 FPS for smooth playback
def video_stream():
    """Fragment that auto-refreshes video feed without reloading the entire page."""

    if not st.session_state.get("tracking_active", False):
        st.info("⏸️ Tracking stopped. Click Start to begin.")
        return

    camera_manager = st.session_state.camera_manager
    hand_tracker = st.session_state.hand_tracker
    selected_camera = st.session_state.selected_camera
    track_movement = st.session_state.get("track_movement", True)
    robot_control_enabled = st.session_state.get("robot_control_enabled", False)
    center_on_target = st.session_state.get("center_on_target", True)

    # Get frame with hand tracking
    if track_movement:
        result = get_hand_tracked_frame(
            selected_camera,
            camera_manager,
            hand_tracker,
            track_movement=True,
            prev_positions=st.session_state.prev_hand_positions
        )
        image, movements, current_positions = result

        if image:
            st.image(image, use_container_width=True, channels="RGB")

            # Update previous positions
            if current_positions:
                st.session_state.prev_hand_positions = current_positions

            # Display stats
            if movements:
                stats_text = f"**Tracking:** {len(movements)} hand(s) moving\n\n"
                for movement in movements:
                    stats_text += f"- **{movement['side'].title()}:** {movement['direction']} ({movement['distance']:.0f}px)\n"
                st.session_state.stats_display = stats_text

                # Robot control
                if robot_control_enabled:
                    if center_on_target:
                        # Center robot on detected hand
                        center_robot_on_hands(current_positions, st.session_state.robot_arm)
                    else:
                        # Follow movement
                        control_robot_from_movement(movements, st.session_state.robot_arm)
            else:
                st.session_state.stats_display = "**Status:** No movement detected"
    else:
        result = get_hand_tracked_frame(
            selected_camera,
            camera_manager,
            hand_tracker,
            track_movement=False
        )
        image, detections, _ = result

        if image:
            st.image(image, use_container_width=True, channels="RGB")

            # Display stats
            if detections:
                stats_text = f"**Detected:** {len(detections)} hand(s)\n\n"
                for det in detections:
                    stats_text += f"- **{det['side'].title()}:** ({det['position'][0]}, {det['position'][1]}) [{det['confidence']:.0%}]\n"
                st.session_state.stats_display = stats_text

                # Robot control
                if robot_control_enabled and center_on_target:
                    # Extract hand positions
                    positions = {det['side']: det['position'] for det in detections}
                    center_robot_on_hands(positions, st.session_state.robot_arm)
            else:
                st.session_state.stats_display = "**Status:** No hands detected"


def main():
    st.title(f"{Icons.HAND} Hand Tracking with YOLO Pose")

    # Initialize session state
    if "tracking_active" not in st.session_state:
        st.session_state.tracking_active = False
    if "prev_hand_positions" not in st.session_state:
        st.session_state.prev_hand_positions = {}
    if "stats_display" not in st.session_state:
        st.session_state.stats_display = "**Status:** Ready"

    # Initialize components
    if "camera_manager" not in st.session_state:
        with st.spinner("Initializing camera..."):
            st.session_state.camera_manager = CameraManager()
        if st.session_state.camera_manager.cameras:
            st.success(f"✅ {len(st.session_state.camera_manager.cameras)} camera(s) detected")
        else:
            st.error("❌ No cameras detected!")
            return

    if "hand_tracker" not in st.session_state:
        with st.spinner("Loading YOLO pose model (first run downloads model)..."):
            st.session_state.hand_tracker = HandTracker(
                model_path="yolov8n-pose.pt",
                score_thr=config.HAND_SCORE_THRESHOLD
            )
        st.success("✅ Hand tracking model loaded!")

    if "robot_arm" not in st.session_state:
        st.session_state.robot_arm = RobotArmController()

    # Sidebar controls
    with st.sidebar:
        st.header("⚙️ Settings")

        # Camera selection
        cameras = st.session_state.camera_manager.cameras
        if not cameras:
            st.error("No cameras available")
            return

        selected_camera = st.selectbox(
            "📷 Camera",
            cameras,
            index=0,
            key="camera_selector"
        )
        st.session_state.selected_camera = selected_camera
        st.session_state.camera_manager.open_capture(selected_camera)

        st.markdown("---")

        # Tracking settings
        st.subheader("📍 Tracking")
        st.session_state.track_movement = st.checkbox(
            "Track Movement",
            value=True,
            help="Track hand movement between frames with arrows"
        )

        confidence = st.slider(
            "Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=config.HAND_SCORE_THRESHOLD,
            step=0.05,
            help="Minimum confidence for hand detection"
        )
        st.session_state.hand_tracker.score_thr = confidence

        st.markdown("---")

        # Robot control
        st.subheader("🤖 Robot Control")
        robot_enabled = st.checkbox("Enable Robot Control", value=False)
        st.session_state.robot_control_enabled = robot_enabled

        if robot_enabled:
            display_robot_status(st.session_state.robot_arm)

            st.session_state.center_on_target = st.checkbox(
                "🎯 Center on Target",
                value=True,
                help="Point robot toward center of detected hand/person"
            )

            if st.session_state.center_on_target:
                st.info("🎯 Robot will point toward and center on detected hands")

                # Centering sensitivity
                st.session_state.center_smoothing = st.slider(
                    "Smoothing",
                    min_value=0.1,
                    max_value=1.0,
                    value=0.5,
                    step=0.1,
                    help="Lower = smoother movement, Higher = more responsive"
                )
            else:
                st.info("🕹️ Robot will follow hand movements")

        st.markdown("---")

        # Statistics
        st.subheader("📊 Statistics")
        st.markdown(st.session_state.stats_display)

    # Main content area
    st.markdown("""
    **Instructions:**
    - Stand 2-6 feet from camera with hands visible
    - Good lighting helps detection accuracy
    - **Track Movement**: Shows motion arrows and direction
    - **Center on Target**: Robot points toward hand center (smooth)
    """)

    # Control buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("▶️ Start Tracking", use_container_width=True, type="primary"):
            st.session_state.tracking_active = True
            st.rerun()

    with col2:
        if st.button("⏹️ Stop Tracking", use_container_width=True):
            st.session_state.tracking_active = False
            st.rerun()

    with col3:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.prev_hand_positions = {}
            st.session_state.stats_display = "**Status:** Reset"
            st.rerun()

    st.markdown("---")

    # Video display area (fragment auto-refreshes this)
    st.subheader("📹 Live Feed")
    video_stream()

    # Footer
    if st.session_state.tracking_active:
        st.caption("🔴 Live • Auto-refreshing at 10 FPS")
    else:
        st.caption("⚫ Stopped • Click Start to begin tracking")


def center_robot_on_hands(
    hand_positions: Dict[str, Tuple[int, int]],
    robot_arm: RobotArmController
) -> None:
    """
    Center robot on detected hands by pointing toward the middle of all detected hands.
    Smoothly adjusts robot position to keep target centered.

    Args:
        hand_positions: Dictionary mapping 'left'/'right' to (x, y) pixel coordinates
        robot_arm: RobotArmController instance
    """
    if not robot_arm.is_port_available() or not hand_positions:
        return

    # Calculate center of all detected hands
    all_positions = list(hand_positions.values())
    center_x = sum(pos[0] for pos in all_positions) / len(all_positions)
    center_y = sum(pos[1] for pos in all_positions) / len(all_positions)

    # Assume camera resolution (adjust if needed)
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480

    # Calculate frame center
    frame_center_x = CAMERA_WIDTH / 2
    frame_center_y = CAMERA_HEIGHT / 2

    # Calculate offset from center (in pixels)
    offset_x = center_x - frame_center_x
    offset_y = center_y - frame_center_y

    # Map pixel offsets to robot coordinates
    # Normalize to -1.0 to 1.0 range
    norm_offset_x = offset_x / frame_center_x
    norm_offset_y = offset_y / frame_center_y

    # Convert to robot workspace coordinates
    # The robot should point toward the hand position
    robot_x = config.DRAW_ORIGIN_X + (center_x / CAMERA_WIDTH) * config.ROBOT_WORKSPACE_WIDTH
    robot_y = config.DRAW_ORIGIN_Y + (center_y / CAMERA_HEIGHT) * config.ROBOT_WORKSPACE_HEIGHT
    robot_z = config.Z_UP  # Keep at safe height

    # Calculate robot base rotation to point toward target
    # Assuming robot base can rotate (motor 1 controls base rotation)
    # Convert pixel offset to angle adjustment
    base_angle_adjustment = norm_offset_x * 45  # Max 45 degree adjustment

    # Get smoothing factor (lower = smoother, higher = more responsive)
    smoothing = st.session_state.get("center_smoothing", 0.5)

    # Apply smoothing to prevent jittery movement
    if "last_robot_x" in st.session_state:
        robot_x = st.session_state.last_robot_x + (robot_x - st.session_state.last_robot_x) * smoothing
        robot_y = st.session_state.last_robot_y + (robot_y - st.session_state.last_robot_y) * smoothing
        base_angle_adjustment = st.session_state.last_base_angle + (base_angle_adjustment - st.session_state.last_base_angle) * smoothing

    # Store for next smoothing calculation
    st.session_state.last_robot_x = robot_x
    st.session_state.last_robot_y = robot_y
    st.session_state.last_base_angle = base_angle_adjustment

    # Send commands to robot
    # 1. Rotate base to point toward target
    robot_arm.point_to_angle(joint=1, angle=base_angle_adjustment, speed=smoothing * 20, acc=10)

    # 2. Move end effector to target position
    robot_arm.pick_up(robot_x, robot_y, robot_z, t=config.T_ANGLE, speed=smoothing)


def control_robot_from_movement(movements: list, robot_arm: RobotArmController) -> None:
    """
    Control robot based on hand movement directions.

    Args:
        movements: List of movement dicts with 'side', 'direction', 'distance'
        robot_arm: RobotArmController instance
    """
    if not robot_arm.is_port_available():
        return

    for movement in movements:
        if movement['side'] == 'right' and movement['distance'] > 20:
            direction = movement['direction']

            if direction == "up":
                robot_arm.point_to_angle(joint=2, angle=45, speed=10)
            elif direction == "down":
                robot_arm.point_to_angle(joint=2, angle=-45, speed=10)
            elif direction == "left":
                robot_arm.point_to_angle(joint=1, angle=45, speed=10)
            elif direction == "right":
                robot_arm.point_to_angle(joint=1, angle=-45, speed=10)


if __name__ == "__main__":
    main()

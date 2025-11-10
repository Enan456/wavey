import streamlit as st
import cv2
from PIL import Image
import json
import serial
from serial.tools import list_ports

################################
# 1. CUSTOM CSS to widen the page
################################
st.markdown(
    """
    <style>
    /* Make the main container about 90% width for a wider layout */
    .block-container {
        max-width: 90% !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

################################
# 2. DETECT CAMERAS ONCE
################################
def list_active_cameras():
    """Scan up to 10 indices, return those that are active. Called only on first load."""
    active = []
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            active.append(i)
            cap.release()
    return active

##########################################
# 3. OPEN AND STORE CAPTURES IN SESSION
##########################################
def open_capture(camera_index):
    """Open a VideoCapture for a given index and store it in session_state."""
    if "camera_caps" not in st.session_state:
        st.session_state.camera_caps = {}
    if camera_index not in st.session_state.camera_caps:
        cap = cv2.VideoCapture(camera_index)
        st.session_state.camera_caps[camera_index] = cap

############################################
# 4. GET FRAME OR FALL BACK TO LAST DISPLAY
############################################
def get_continuous_frame(camera_index):
    """
    Retrieve a single frame from an already-open cv2.VideoCapture in session_state.
    If camera fails to produce a new frame, return the previously stored frame
    to avoid a white or empty space.
    """
    # The last known good frame is stored under "frame_{camera_index}"
    fallback_frame = st.session_state.get(f"frame_{camera_index}", None)

    cap = st.session_state.camera_caps.get(camera_index, None)
    if not cap or not cap.isOpened():
        # If the cap is missing or closed, just return our fallback
        return fallback_frame

    ret, frame = cap.read()
    if ret:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(frame_rgb)
        # Store new frame as the last displayed
        st.session_state[f"frame_{camera_index}"] = pil_img
        return pil_img
    else:
        # No new frame, return fallback
        return fallback_frame

##################################
# 5. SEND COMMAND TO ROBOTIC ARM
##################################
def send_command(command, port):
    """Send a JSON command to the robotic arm via USB serial."""
    try:
        with serial.Serial(port, baudrate=115200, timeout=1) as ser:
            ser.write((json.dumps(command) + "\n").encode())
        st.success(f"Command sent: {command}")
    except Exception as e:
        st.error(f"Failed to send command: {e}")

###############################################################
# 6. PARTIAL-PAGE REFRESH FRAGMENT FOR DUAL CAMERA STREAMS
###############################################################
@st.fragment(run_every="200ms")  # ~5 times per second
def dual_webcam_stream():
    """Display camera feeds with fallback to last displayed frame if new frame is missing."""
    st.subheader("Dual Webcam Feeds")

    # Retrieve the chosen cameras
    cam1 = st.session_state.get("selected_cam1", None)
    cam2 = st.session_state.get("selected_cam2", None)

    if cam1 is None and cam2 is None:
        st.warning("No cameras selected or no active cameras found.")
        return

    # 2 columns for two camera feeds
    col_cam1, col_cam2 = st.columns(2)

    with col_cam1:
        st.markdown("### Camera 1")
        if cam1 is not None:
            frame1 = get_continuous_frame(cam1)
            if frame1:
                st.image(frame1, use_container_width=True)
            else:
                st.warning(f"No frame available from camera {cam1}")
        else:
            st.warning("Camera 1 not selected.")

    with col_cam2:
        st.markdown("### Camera 2")
        if cam2 is not None:
            frame2 = get_continuous_frame(cam2)
            if frame2:
                st.image(frame2, use_container_width=True)
            else:
                st.warning(f"No frame available from camera {cam2}")
        else:
            st.warning("Camera 2 not selected.")

###################################
# 7. ROBOTIC ARM CONTROL FUNCTIONS
###################################
def robotic_arm_controls(robot_arm_port):
    """User interface for controlling the robotic arm."""
    st.markdown("## Robotic Arm Controls")
    st.markdown("### Motor Control Sliders")

    motor_angles = {}
    for motor_id in range(1, 5):
        motor_angles[motor_id] = st.slider(
            f"Motor {motor_id} Angle (degrees)",
            min_value=-180,
            max_value=180,
            value=0
        )

    if st.button("Send Motor Angles"):
        command = {"T": 999, "angles": motor_angles}
        send_command(command, robot_arm_port)

    st.markdown("### Predefined Actions")

    # Open/Close Hand
    st.markdown("#### Open/Close Hand")
    open_angle = st.number_input("Open Angle (radians)", value=3.14, key="open_angle")
    if st.button("Run Open", key="open_hand"):
        command = {"T": 106, "cmd": open_angle, "spd": 0.5, "acc": 10}
        send_command(command, robot_arm_port)

    close_angle = st.number_input("Close Angle (radians)", value=1.2, key="close_angle")
    if st.button("Run Close", key="close_hand"):
        command = {"T": 106, "cmd": close_angle, "spd": 0.5, "acc": 10}
        send_command(command, robot_arm_port)

    # Point to Angle
    st.markdown("#### Point to Angle")
    base_angle = st.number_input("Base Angle (degrees)", value=90, key="base_angle")
    if st.button("Run Angle", key="point_to_angle"):
        command = {"T": 121, "joint": 1, "angle": base_angle, "spd": 10, "acc": 10}
        send_command(command, robot_arm_port)

    # Pick Up
    st.markdown("#### Pick Up Object")
    x = st.number_input("X Coordinate (mm)", value=200, key="x_coord")
    y = st.number_input("Y Coordinate (mm)", value=0, key="y_coord")
    z = st.number_input("Z Coordinate (mm)", value=50, key="z_coord")
    if st.button("Run Pick Up", key="pick_up"):
        command = {"T": 104, "x": x, "y": y, "z": z, "t": 1.57, "spd": 0.5}
        send_command(command, robot_arm_port)

    # Draw on Table
    st.markdown("#### Draw on Table")
    start_x = st.number_input("Start X (mm)", value=100, key="start_x")
    start_y = st.number_input("Start Y (mm)", value=100, key="start_y")
    end_x = st.number_input("End X (mm)", value=200, key="end_x")
    end_y = st.number_input("End Y (mm)", value=200, key="end_y")
    if st.button("Run Draw", key="draw_on_table"):
        command_start = {
            "T": 104,
            "x": start_x,
            "y": start_y,
            "z": 50,
            "t": 1.57,
            "spd": 0.5
        }
        command_end = {
            "T": 104,
            "x": end_x,
            "y": end_y,
            "z": 50,
            "t": 1.57,
            "spd": 0.5
        }
        send_command(command_start, robot_arm_port)
        send_command(command_end, robot_arm_port)

#####################
# 8. MAIN APPLICATION
#####################
def main():
    st.title("Robotic Arm Control & Dual Camera Feeds (With Fallback Frames)")

    # On first load, detect cameras once
    if "available_cameras" not in st.session_state:
        st.session_state.available_cameras = list_active_cameras()

    # Create columns: 20% for controls, 80% for camera feeds
    col_controls, col_cams = st.columns([0.2, 0.8])

    with col_controls:
        # Detect robotic arm port
        robot_arm_port = None
        for port in list_ports.comports():
            if "usb" in port.device.lower() or "tty" in port.device.lower():
                robot_arm_port = port.device
                break

        if robot_arm_port:
            robotic_arm_controls(robot_arm_port)
        else:
            st.error("Robotic Arm not detected. Please connect the device and restart.")

    with col_cams:
        cameras = st.session_state.available_cameras
        if not cameras:
            st.warning("No active cameras were detected on initial load.")
        else:
            # If no default set, pick first or second camera
            if "selected_cam1" not in st.session_state:
                st.session_state.selected_cam1 = cameras[0]
            if "selected_cam2" not in st.session_state:
                st.session_state.selected_cam2 = cameras[0] if len(cameras) == 1 else cameras[1]

            # Let the user pick camera indices
            st.session_state.selected_cam1 = st.selectbox(
                "Select Camera 1",
                cameras,
                index=cameras.index(st.session_state.selected_cam1),
            )
            st.session_state.selected_cam2 = st.selectbox(
                "Select Camera 2",
                cameras,
                index=cameras.index(st.session_state.selected_cam2),
            )

            # Open the captures if not already open
            open_capture(st.session_state.selected_cam1)
            open_capture(st.session_state.selected_cam2)

        # Display the cameras with partial-page refresh
        dual_webcam_stream()

if __name__ == "__main__":
    main()

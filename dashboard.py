import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx

# Local imports
from utils.robot_ops import RobotArmController
from utils.video_processing import CameraManager, YOLOModel, get_annotated_frame

# For partial refresh (if using some extension like st.fragment):
try:
    from streamlit_extras.fragment import fragment
except ImportError:
    # If you don't have a specialized fragment decorator,
    # you can just define a no-op decorator for demonstration
    def fragment(run_every=None):
        def decorator(func):
            return func
        return decorator

################################
# CUSTOM CSS to widen the page
################################
st.markdown(
    """
    <style>
    .block-container {
        max-width: 90% !important; /* Widen layout to ~90% */
    }
    </style>
    """,
    unsafe_allow_html=True
)

#################################
# PARTIAL REFRESH FOR DUAL FEEDS
#################################
@fragment(run_every="1000ms")  # Attempt to refresh once per second
def dual_webcam_stream():
    st.subheader("Dual Webcam Feeds (YOLO @ ~1 FPS)")

    cam1 = st.session_state.get("selected_cam1", None)
    cam2 = st.session_state.get("selected_cam2", None)

    if cam1 is None and cam2 is None:
        st.warning("No cameras selected or no active cameras found.")
        return

    col_cam1, col_cam2 = st.columns(2)

    with col_cam1:
        st.markdown("### Camera 1")
        if cam1 is not None:
            frame1 = get_annotated_frame(
                cam1,
                st.session_state.camera_manager,
                st.session_state.yolo_model
            )
            if frame1:
                st.image(frame1, use_container_width=True)
            else:
                st.warning(f"No frame available from camera {cam1}")
        else:
            st.warning("Camera 1 not selected.")

    with col_cam2:
        st.markdown("### Camera 2")
        if cam2 is not None:
            frame2 = get_annotated_frame(
                cam2,
                st.session_state.camera_manager,
                st.session_state.yolo_model
            )
            if frame2:
                st.image(frame2, use_container_width=True)
            else:
                st.warning(f"No frame available from camera {cam2}")
        else:
            st.warning("Camera 2 not selected.")

def show_robotic_arm_controls(robot_arm):
    """
    Streamlit UI for controlling the robotic arm. Uses methods from RobotArmController.
    """
    st.markdown("## Robotic Arm Controls")
    st.markdown("### Motor Control Sliders")

    motor_angles = {}
    for motor_id in range(1, 5):
        motor_angles[motor_id] = st.slider(
            f"Motor {motor_id} Angle (degrees)",
            min_value=-180,
            max_value=180,
            value=0,
            key=f"motor_{motor_id}"
        )

    if st.button("Send Motor Angles"):
        robot_arm.set_motor_angles(motor_angles)

    st.markdown("### Predefined Actions")

    # Open/Close Hand
    st.markdown("#### Open/Close Hand")
    open_angle = st.number_input("Open Angle (radians)", value=3.14, key="open_angle")
    if st.button("Run Open", key="open_hand"):
        robot_arm.open_hand(open_angle)

    close_angle = st.number_input("Close Angle (radians)", value=1.2, key="close_angle")
    if st.button("Run Close", key="close_hand"):
        robot_arm.close_hand(close_angle)

    # Point to Angle
    st.markdown("#### Point to Angle")
    base_angle = st.number_input("Base Angle (degrees)", value=90, key="base_angle")
    if st.button("Run Angle", key="point_to_angle"):
        robot_arm.point_to_angle(angle=base_angle)

    # Pick Up
    st.markdown("#### Pick Up Object")
    x = st.number_input("X Coordinate (mm)", value=200, key="x_coord")
    y = st.number_input("Y Coordinate (mm)", value=0, key="y_coord")
    z = st.number_input("Z Coordinate (mm)", value=50, key="z_coord")
    if st.button("Run Pick Up", key="pick_up"):
        robot_arm.pick_up(x, y, z)

    # Draw on Table
    st.markdown("#### Draw on Table")
    start_x = st.number_input("Start X (mm)", value=100, key="start_x")
    start_y = st.number_input("Start Y (mm)", value=100, key="start_y")
    end_x = st.number_input("End X (mm)", value=200, key="end_x")
    end_y = st.number_input("End Y (mm)", value=200, key="end_y")
    if st.button("Run Draw", key="draw_on_table"):
        robot_arm.draw_on_table(start_x, start_y, end_x, end_y)

def main():
    # Title
    st.title("Robotic Arm Control & Dual Camera Feeds with YOLO")

    # Initialize RobotArmController in session_state if not present
    if "robot_arm" not in st.session_state:
        st.session_state.robot_arm = RobotArmController()

    # Initialize CameraManager once
    if "camera_manager" not in st.session_state:
        st.session_state.camera_manager = CameraManager()

    # Initialize and store a YOLO model (trained on COCO)
    if "yolo_model" not in st.session_state:
        # Default YOLO model on COCO (yolov8n.pt, yolov8s.pt, etc.)
        MODEL_PATH = "yolov8n.pt"  # or an absolute path
        SCORE_THRESHOLD = 0.3

        st.session_state.yolo_model = YOLOModel(
            model_path=MODEL_PATH,
            device="cuda",     # or "cpu"
            score_thr=SCORE_THRESHOLD
        )
        st.success("YOLO model loaded successfully!")

    # Layout: 20% controls / 80% cameras
    col_controls, col_cams = st.columns([0.2, 0.8])

    with col_controls:
        # Show the robot arm UI
        robot_arm = st.session_state.robot_arm
        if robot_arm.is_port_available():
            show_robotic_arm_controls(robot_arm)
        else:
            st.error("Robotic Arm not detected. Please connect and restart.")

    with col_cams:
        # Let the user pick cameras
        camera_manager = st.session_state.camera_manager
        cameras = camera_manager.cameras

        if not cameras:
            st.warning("No active cameras were detected.")
        else:
            # Default selections
            if "selected_cam1" not in st.session_state:
                st.session_state.selected_cam1 = cameras[0]
            if "selected_cam2" not in st.session_state:
                st.session_state.selected_cam2 = cameras[0] if len(cameras) == 1 else cameras[1]

            st.session_state.selected_cam1 = st.selectbox(
                "Select Camera 1",
                cameras,
                index=cameras.index(st.session_state.selected_cam1)
            )
            st.session_state.selected_cam2 = st.selectbox(
                "Select Camera 2",
                cameras,
                index=cameras.index(st.session_state.selected_cam2)
            )

            # Open captures
            camera_manager.open_capture(st.session_state.selected_cam1)
            camera_manager.open_capture(st.session_state.selected_cam2)

            # Start the partial-refresh fragment that displays cameras
            dual_webcam_stream()

if __name__ == "__main__":
    main()

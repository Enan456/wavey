"""
Drawing application for robot arm control.
Allows users to draw on a canvas and have the robot replicate the drawing.
"""

import streamlit as st
from streamlit_drawable_canvas import st_canvas

# Local imports
import config
from utils.robot_ops import RobotArmController
from utils.canvas_utils import (
    parse_canvas_strokes_and_rectangles,
    scale_and_offset_points,
    send_drawing_instructions,
    pick_up_at_rectangle_centers
)
from utils.ui_config import display_robot_status


def main():
    st.title("🤖 Robot Arm Drawing Interface")

    # Initialize RobotArmController in session state
    if "robot_arm" not in st.session_state:
        st.session_state.robot_arm = RobotArmController()

    robot_arm = st.session_state.robot_arm

    # Display robot connection status
    display_robot_status(robot_arm)

    # Check if robot arm is available
    if not robot_arm.is_port_available():
        st.warning("⚠️ Robotic Arm not detected. Please connect and refresh the page.")
        return

    # Instructions
    st.markdown("""
    ### Instructions
    1. **Freedraw** on the canvas to create lines the robot will draw with a pen
    2. **Draw rectangles** (use shape tool) to mark pick-up locations
    3. Click **"Send to Robot"** to execute the drawing

    The canvas coordinates will be automatically scaled to robot workspace coordinates.
    """)

    # Canvas configuration display
    with st.expander("⚙️ Configuration", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Canvas Size:** {config.CANVAS_WIDTH}x{config.CANVAS_HEIGHT} px")
            st.write(f"**Robot Workspace:** {config.ROBOT_WORKSPACE_WIDTH}x{config.ROBOT_WORKSPACE_HEIGHT} mm")
        with col2:
            st.write(f"**Z Up:** {config.Z_UP} mm")
            st.write(f"**Z Down:** {config.Z_DOWN} mm")
            st.write(f"**Z Pickup:** {config.Z_PICKUP} mm")

    # Create drawable canvas
    drawing_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",  # Transparent fill
        stroke_width=config.DEFAULT_STROKE_WIDTH,
        stroke_color=config.DEFAULT_STROKE_COLOR,
        background_color="#FFFFFF",
        update_streamlit=True,
        height=config.CANVAS_HEIGHT,
        width=config.CANVAS_WIDTH,
        drawing_mode="freedraw",
        key="canvas",
    )

    # Send to robot button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        send_button = st.button("🚀 Send to Robot", use_container_width=True, type="primary")

    if send_button:
        if drawing_result.json_data is None:
            st.warning("Please draw something on the canvas first!")
            return

        with st.spinner("Processing drawing and sending to robot..."):
            # Parse strokes and rectangles from canvas
            strokes, rectangles = parse_canvas_strokes_and_rectangles(drawing_result.json_data)

            if not strokes and not rectangles:
                st.warning("No drawing data found. Please draw on the canvas.")
                return

            # Scale and offset strokes for drawing
            scaled_strokes = []
            for stroke in strokes:
                scaled_strokes.append(scale_and_offset_points(stroke))

            # Display what was detected
            st.info(f"📝 Detected: {len(strokes)} stroke(s) and {len(rectangles)} rectangle(s)")

            # Send drawing instructions
            if scaled_strokes:
                send_drawing_instructions(robot_arm, scaled_strokes)

            # Send pickup instructions for rectangles
            if rectangles:
                pick_up_at_rectangle_centers(robot_arm, rectangles)

            st.success("✅ Drawing & pickup instructions sent to robot arm!")
            st.balloons()


if __name__ == "__main__":
    main()

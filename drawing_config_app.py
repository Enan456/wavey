import streamlit as st
from streamlit_drawable_canvas import st_canvas

# Assume robot_ops.py exists in the same directory with a RobotArmController class
from utils.robot_ops import RobotArmController

#######################################
# 1. Configuration / Constants
#######################################

# Default values
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
SCALE_X = 300 / CANVAS_WIDTH
SCALE_Y = 225 / CANVAS_HEIGHT
DRAW_ORIGIN_X = 100
DRAW_ORIGIN_Y = 100
Z_UP = 80
Z_DOWN = 50
T_ANGLE = 1.57

# Streamlit UI
st.title("Robot Arm Configuration")

st.sidebar.header("Canvas Settings")
CANVAS_WIDTH = st.sidebar.number_input("Canvas Width", value=CANVAS_WIDTH)
CANVAS_HEIGHT = st.sidebar.number_input("Canvas Height", value=CANVAS_HEIGHT)

st.sidebar.header("Scaling Settings")
SCALE_X = st.sidebar.number_input("Scale X", value=SCALE_X)
SCALE_Y = st.sidebar.number_input("Scale Y", value=SCALE_Y)

st.sidebar.header("Drawing Origin")
DRAW_ORIGIN_X = st.sidebar.number_input("Draw Origin X", value=DRAW_ORIGIN_X)
DRAW_ORIGIN_Y = st.sidebar.number_input("Draw Origin Y", value=DRAW_ORIGIN_Y)

st.sidebar.header("Pen Positions")
Z_UP = st.sidebar.number_input("Pen Up Position (Z)", value=Z_UP)
Z_DOWN = st.sidebar.number_input("Pen Down Position (Z)", value=Z_DOWN)

st.sidebar.header("End Effector Orientation")
T_ANGLE = st.sidebar.number_input("End Effector Angle (rad)", value=T_ANGLE)

# Display current configuration
st.write("## Current Configuration")
st.write(f"Canvas Width: {CANVAS_WIDTH}")
st.write(f"Canvas Height: {CANVAS_HEIGHT}")
st.write(f"Scale X: {SCALE_X}")
st.write(f"Scale Y: {SCALE_Y}")
st.write(f"Draw Origin X: {DRAW_ORIGIN_X}")
st.write(f"Draw Origin Y: {DRAW_ORIGIN_Y}")
st.write(f"Pen Up Position (Z): {Z_UP}")
st.write(f"Pen Down Position (Z): {Z_DOWN}")
st.write(f"End Effector Angle (rad): {T_ANGLE}")

# Initialize RobotArmController with the current configuration
robot_arm = RobotArmController(
    width=CANVAS_WIDTH,
    height=CANVAS_HEIGHT,
    scale_x=SCALE_X,
    scale_y=SCALE_Y,
    origin_x=DRAW_ORIGIN_X,
    origin_y=DRAW_ORIGIN_Y,
    z_up=Z_UP,
    z_down=Z_DOWN,
    angle=T_ANGLE
)

# Add a button to test the configuration
if st.button("Test Configuration"):
    st.write("Testing configuration...")
    # Add your testing logic here
    # For example, move the robot arm to the origin
    robot_arm.move_to(DRAW_ORIGIN_X, DRAW_ORIGIN_Y, Z_UP)
    st.write("Configuration tested successfully.")

###########################################
# 2. Helper functions to parse and send data
###########################################

def parse_canvas_strokes_and_rectangles(json_data):
    """
    Given the JSON-like data from st_canvas, parse out:
      1) Freedraw strokes ("path" type) => lines for drawing
      2) Rectangles => treat as a "pick-up" location
    Returns:
      strokes: list of [ (x1,y1), (x2,y2), ... ] for each stroke
      rectangles: list of { 'left': ..., 'top': ..., 'width': ..., 'height': ... }
    """
    if not json_data or "objects" not in json_data:
        return [], []

    strokes = []
    rectangles = []

    for obj in json_data["objects"]:
        obj_type = obj["type"]

        # Freedraw lines
        if obj_type == "path":
            path = obj["path"]  # e.g. [['M', x, y], ['L', x, y], ...]
            points = []
            for segment in path:
                cmd = segment[0]
                if cmd in ("M", "L"):  # Move or Line
                    x, y = segment[1], segment[2]
                    points.append((x, y))
            if points:
                strokes.append(points)

        # Rectangles
        elif obj_type == "rect":
            left = obj["left"]
            top = obj["top"]
            width = obj["width"]
            height = obj["height"]
            rectangles.append({
                "left": left,
                "top": top,
                "width": width,
                "height": height
            })

    return strokes, rectangles

def scale_and_offset_points(points):
    """
    Takes a list of (x, y) in canvas coordinates [0..CANVAS_WIDTH],
    scales and offsets them into robot coordinates.
    """
    scaled = []
    for (px, py) in points:
        rx = DRAW_ORIGIN_X + px * SCALE_X
        ry = DRAW_ORIGIN_Y + py * SCALE_Y
        scaled.append((rx, ry))
    return scaled

def send_drawing_instructions(robot_arm, strokes):
    """
    Sends a series of commands to the robot arm to replicate the drawn strokes.
    For each stroke:
      1. Move pen up
      2. Move to first point
      3. Move pen down
      4. Move along stroke
      5. Pen up again at end
    """
    def move_to(x, y, z):
        command = {"T": 104, "x": x, "y": y, "z": z, "t": T_ANGLE, "spd": 0.5}
        robot_arm.send_command(command)

    for stroke in strokes:
        if not stroke:
            continue

        # 1) Pen up
        first_x, first_y = stroke[0]
        move_to(first_x, first_y, Z_UP)

        # 3) Pen down
        move_to(first_x, first_y, Z_DOWN)

        # 4) Move along the stroke with pen down
        for (x, y) in stroke[1:]:
            move_to(x, y, Z_DOWN)

        # 5) Pen up at end
        last_x, last_y = stroke[-1]
        move_to(last_x, last_y, Z_UP)

def pick_up_at_rectangle_centers(robot_arm, rectangles):
    """
    For each rectangle, find the center point and command the robot to pick up there.
    """
    for rect in rectangles:
        left = rect["left"]
        top = rect["top"]
        width = rect["width"]
        height = rect["height"]

        # Center in canvas coordinates
        center_x = left + (width / 2)
        center_y = top + (height / 2)

        # Scale and offset
        robot_x = DRAW_ORIGIN_X + center_x * SCALE_X
        robot_y = DRAW_ORIGIN_Y + center_y * SCALE_Y

        # Use the pick_up method or a custom command
        # We'll do a simple approach: move above, then descend
        # *You can refine to pen up/pen down logic or any approach for "pick up."

        # Move above
        command_up = {
            "T": 104,
            "x": robot_x,
            "y": robot_y,
            "z": Z_UP,
            "t": T_ANGLE,
            "spd": 0.5
        }
        robot_arm.send_command(command_up)

        # Move down
        command_down = {
            "T": 104,
            "x": robot_x,
            "y": robot_y,
            "z": Z_PICKUP,
            "t": T_ANGLE,
            "spd": 0.5
        }
        robot_arm.send_command(command_down)

        # Actual pick up command, if your robot firmware expects it
        # If you have a specific "pick_up" method:
        #   robot_arm.pick_up(robot_x, robot_y, Z_PICKUP, t=T_ANGLE, speed=0.5)
        # Or for a simple approach, do a close hand command:
        close_command = {"T": 106, "cmd": 1.2, "spd": 0.5, "acc": 10}
        robot_arm.send_command(close_command)

        # Lift back up
        robot_arm.send_command(command_up)

#################################
# 3. The Streamlit App
#################################
def main():
    st.title("Draw & In Blank Space Pick It Up")

    # Instantiate RobotArmController
    if "robot_arm" not in st.session_state:
        st.session_state.robot_arm = RobotArmController()

    robot_arm = st.session_state.robot_arm

    # Check if robot arm is available
    if not robot_arm.is_port_available():
        st.error("Robotic Arm not detected. Please connect and restart.")
        return

    st.markdown("""
    **Instructions**:
    1. Freedraw on the canvas for lines you want the robot to plot with a pen.
    2. Draw **rectangles** (use the shape tool in the toolbar) where you want the robot to pick up an item.
    3. Click "Send to Robot" to transform your drawings into robot instructions.
    """)

    # Create a larger canvas component
    drawing_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",  # Transparent fill
        stroke_width=2,
        stroke_color="#000000",
        background_color="#FFFFFF",
        update_streamlit=True,
        height=CANVAS_HEIGHT,
        width=CANVAS_WIDTH,
        drawing_mode="freedraw",  # or "transform" to handle shapes, etc.
        key="canvas",
    )

    # If you want the user to be able to draw rectangles easily, 
    # you can pass drawing_mode="transform" so the user can select shape tools in the toolbar.

    if st.button("Send to Robot"):
        # 1) Parse lines + rectangles
        strokes, rectangles = parse_canvas_strokes_and_rectangles(drawing_result.json_data)

        # 2) Scale & offset strokes for drawing
        scaled_strokes = []
        for stroke in strokes:
            scaled_strokes.append(scale_and_offset_points(stroke))

        # 3) Send drawing instructions
        send_drawing_instructions(robot_arm, scaled_strokes)

        # 4) For each rectangle, pick up at center
        pick_up_at_rectangle_centers(robot_arm, rectangles)

        st.success("Drawing & pickup instructions sent to the robot arm!")

if __name__ == "__main__":
    main()

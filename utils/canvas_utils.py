"""
Canvas utility functions for parsing drawable canvas data and converting
coordinates between canvas space and robot workspace.
"""

from typing import List, Tuple, Dict, Any, Optional
import config
from utils.robot_ops import RobotArmController


# Type aliases for better readability
Point = Tuple[float, float]
Stroke = List[Point]
Rectangle = Dict[str, float]


def parse_canvas_strokes_and_rectangles(
    json_data: Optional[Dict[str, Any]]
) -> Tuple[List[Stroke], List[Rectangle]]:
    """
    Parse JSON data from st_canvas to extract drawing strokes and rectangles.

    Args:
        json_data: The JSON-like data from streamlit_drawable_canvas

    Returns:
        A tuple containing:
        - strokes: List of strokes, where each stroke is a list of (x, y) points
        - rectangles: List of rectangle dictionaries with 'left', 'top', 'width', 'height'

    Examples:
        >>> data = {"objects": [{"type": "path", "path": [["M", 10, 20], ["L", 30, 40]]}]}
        >>> strokes, rectangles = parse_canvas_strokes_and_rectangles(data)
        >>> strokes
        [[(10, 20), (30, 40)]]
    """
    if not json_data or "objects" not in json_data:
        return [], []

    strokes: List[Stroke] = []
    rectangles: List[Rectangle] = []

    for obj in json_data["objects"]:
        obj_type = obj.get("type")

        # Freedraw lines (path type)
        if obj_type == "path":
            path = obj.get("path", [])  # e.g. [['M', x, y], ['L', x, y], ...]
            points: Stroke = []

            for segment in path:
                if len(segment) >= 3:
                    cmd = segment[0]
                    if cmd in ("M", "L"):  # Move or Line command
                        x, y = segment[1], segment[2]
                        points.append((x, y))

            if points:
                strokes.append(points)

        # Rectangles
        elif obj_type == "rect":
            rectangles.append({
                "left": obj.get("left", 0),
                "top": obj.get("top", 0),
                "width": obj.get("width", 0),
                "height": obj.get("height", 0)
            })

    return strokes, rectangles


def scale_and_offset_points(
    points: Stroke,
    scale_x: float = config.SCALE_X,
    scale_y: float = config.SCALE_Y,
    origin_x: float = config.DRAW_ORIGIN_X,
    origin_y: float = config.DRAW_ORIGIN_Y
) -> Stroke:
    """
    Convert canvas coordinates to robot workspace coordinates.

    Takes points in canvas pixel coordinates and transforms them to robot
    millimeter coordinates using scaling and offset.

    Args:
        points: List of (x, y) tuples in canvas coordinates
        scale_x: Scaling factor for X axis (mm per pixel)
        scale_y: Scaling factor for Y axis (mm per pixel)
        origin_x: X offset in robot coordinates (mm)
        origin_y: Y offset in robot coordinates (mm)

    Returns:
        List of (x, y) tuples in robot coordinates (mm)

    Examples:
        >>> canvas_points = [(0, 0), (100, 100)]
        >>> robot_points = scale_and_offset_points(canvas_points)
    """
    scaled: Stroke = []
    for px, py in points:
        rx = origin_x + px * scale_x
        ry = origin_y + py * scale_y
        scaled.append((rx, ry))
    return scaled


def send_drawing_instructions(
    robot_arm: RobotArmController,
    strokes: List[Stroke],
    z_up: float = config.Z_UP,
    z_down: float = config.Z_DOWN,
    t_angle: float = config.T_ANGLE,
    speed: float = config.DEFAULT_MOVE_SPEED
) -> None:
    """
    Send commands to robot arm to draw the given strokes.

    For each stroke:
    1. Move pen up to safe height
    2. Move to first point of stroke
    3. Lower pen to drawing height
    4. Trace the stroke
    5. Lift pen up at end

    Args:
        robot_arm: RobotArmController instance
        strokes: List of strokes to draw, each stroke is a list of (x, y) points
        z_up: Z coordinate for pen up position (mm)
        z_down: Z coordinate for pen down/drawing position (mm)
        t_angle: End effector orientation angle (radians)
        speed: Movement speed
    """
    def move_to(x: float, y: float, z: float) -> None:
        """Helper function to send move command."""
        command = {
            "T": config.CMD_MOVE_TO_POSITION,
            "x": x,
            "y": y,
            "z": z,
            "t": t_angle,
            "spd": speed
        }
        robot_arm.send_command(command)

    for stroke in strokes:
        if not stroke:
            continue

        # Move to first point with pen up
        first_x, first_y = stroke[0]
        move_to(first_x, first_y, z_up)

        # Lower pen to drawing position
        move_to(first_x, first_y, z_down)

        # Trace along the stroke with pen down
        for x, y in stroke[1:]:
            move_to(x, y, z_down)

        # Lift pen at end of stroke
        last_x, last_y = stroke[-1]
        move_to(last_x, last_y, z_up)


def pick_up_at_rectangle_centers(
    robot_arm: RobotArmController,
    rectangles: List[Rectangle],
    scale_x: float = config.SCALE_X,
    scale_y: float = config.SCALE_Y,
    origin_x: float = config.DRAW_ORIGIN_X,
    origin_y: float = config.DRAW_ORIGIN_Y,
    z_up: float = config.Z_UP,
    z_pickup: float = config.Z_PICKUP,
    t_angle: float = config.T_ANGLE,
    speed: float = config.DEFAULT_MOVE_SPEED
) -> None:
    """
    Command robot to pick up objects at rectangle center points.

    For each rectangle drawn on canvas:
    1. Calculate center point
    2. Convert to robot coordinates
    3. Move above the point
    4. Descend to pickup height
    5. Close gripper
    6. Lift back up

    Args:
        robot_arm: RobotArmController instance
        rectangles: List of rectangle dictionaries with 'left', 'top', 'width', 'height'
        scale_x: X axis scaling factor
        scale_y: Y axis scaling factor
        origin_x: X offset in robot coordinates
        origin_y: Y offset in robot coordinates
        z_up: Safe height above objects (mm)
        z_pickup: Height to descend to for pickup (mm)
        t_angle: End effector orientation (radians)
        speed: Movement speed
    """
    for rect in rectangles:
        left = rect["left"]
        top = rect["top"]
        width = rect["width"]
        height = rect["height"]

        # Calculate center in canvas coordinates
        center_x = left + (width / 2)
        center_y = top + (height / 2)

        # Convert to robot coordinates
        robot_x = origin_x + center_x * scale_x
        robot_y = origin_y + center_y * scale_y

        # Move above the target
        command_up = {
            "T": config.CMD_MOVE_TO_POSITION,
            "x": robot_x,
            "y": robot_y,
            "z": z_up,
            "t": t_angle,
            "spd": speed
        }
        robot_arm.send_command(command_up)

        # Descend to pickup height
        command_down = {
            "T": config.CMD_MOVE_TO_POSITION,
            "x": robot_x,
            "y": robot_y,
            "z": z_pickup,
            "t": t_angle,
            "spd": speed
        }
        robot_arm.send_command(command_down)

        # Close gripper to grasp object
        close_command = {
            "T": config.CMD_GRIPPER_CONTROL,
            "cmd": config.GRIPPER_CLOSE_ANGLE,
            "spd": config.GRIPPER_SPEED,
            "acc": config.GRIPPER_ACCELERATION
        }
        robot_arm.send_command(close_command)

        # Lift object back up
        robot_arm.send_command(command_up)


def canvas_to_robot_coordinates(
    canvas_x: float,
    canvas_y: float,
    scale_x: float = config.SCALE_X,
    scale_y: float = config.SCALE_Y,
    origin_x: float = config.DRAW_ORIGIN_X,
    origin_y: float = config.DRAW_ORIGIN_Y
) -> Tuple[float, float]:
    """
    Convert a single canvas point to robot coordinates.

    Args:
        canvas_x: X coordinate in canvas space (pixels)
        canvas_y: Y coordinate in canvas space (pixels)
        scale_x: X scaling factor
        scale_y: Y scaling factor
        origin_x: X offset in robot coordinates
        origin_y: Y offset in robot coordinates

    Returns:
        Tuple of (robot_x, robot_y) in millimeters
    """
    robot_x = origin_x + canvas_x * scale_x
    robot_y = origin_y + canvas_y * scale_y
    return robot_x, robot_y


def robot_to_canvas_coordinates(
    robot_x: float,
    robot_y: float,
    scale_x: float = config.SCALE_X,
    scale_y: float = config.SCALE_Y,
    origin_x: float = config.DRAW_ORIGIN_X,
    origin_y: float = config.DRAW_ORIGIN_Y
) -> Tuple[float, float]:
    """
    Convert robot coordinates to canvas coordinates.

    Inverse of canvas_to_robot_coordinates. Useful for visualizing
    robot positions on the canvas.

    Args:
        robot_x: X coordinate in robot space (mm)
        robot_y: Y coordinate in robot space (mm)
        scale_x: X scaling factor
        scale_y: Y scaling factor
        origin_x: X offset in robot coordinates
        origin_y: Y offset in robot coordinates

    Returns:
        Tuple of (canvas_x, canvas_y) in pixels
    """
    canvas_x = (robot_x - origin_x) / scale_x
    canvas_y = (robot_y - origin_y) / scale_y
    return canvas_x, canvas_y

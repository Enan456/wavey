"""
UI configuration and styling utilities for Streamlit applications.
Contains shared CSS, layout configurations, and UI helper functions.
"""

import streamlit as st
from typing import Optional
import config


def apply_wide_layout(max_width: str = config.PAGE_MAX_WIDTH) -> None:
    """
    Apply custom CSS to widen the Streamlit page layout.

    Args:
        max_width: Maximum width as a CSS value (e.g., "90%", "1200px")

    Example:
        >>> apply_wide_layout("95%")
    """
    st.markdown(
        f"""
        <style>
        .block-container {{
            max-width: {max_width} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


def apply_custom_css(css: str) -> None:
    """
    Apply custom CSS styles to the Streamlit app.

    Args:
        css: CSS string to apply

    Example:
        >>> apply_custom_css("body { font-family: 'Arial'; }")
    """
    st.markdown(
        f"""
        <style>
        {css}
        </style>
        """,
        unsafe_allow_html=True
    )


def create_header(title: str, subtitle: Optional[str] = None) -> None:
    """
    Create a standardized header with optional subtitle.

    Args:
        title: Main header text
        subtitle: Optional subtitle text

    Example:
        >>> create_header("Robot Control", "Version 1.0")
    """
    st.title(title)
    if subtitle:
        st.markdown(f"*{subtitle}*")


def create_section_divider(text: Optional[str] = None) -> None:
    """
    Create a visual section divider with optional text.

    Args:
        text: Optional text to display in the divider

    Example:
        >>> create_section_divider("Camera Controls")
    """
    if text:
        st.markdown(f"---\n### {text}")
    else:
        st.markdown("---")


def show_status_indicator(
    label: str,
    status: bool,
    success_text: str = "Active",
    failure_text: str = "Inactive"
) -> None:
    """
    Display a status indicator with colored badge.

    Args:
        label: Label for the status
        status: True for success/active, False for failure/inactive
        success_text: Text to show when status is True
        failure_text: Text to show when status is False

    Example:
        >>> show_status_indicator("Robot Arm", robot.is_connected(), "Connected", "Disconnected")
    """
    if status:
        st.success(f"{label}: {success_text}")
    else:
        st.error(f"{label}: {failure_text}")


def create_info_card(title: str, content: str, icon: str = "ℹ️") -> None:
    """
    Create an info card with title and content.

    Args:
        title: Card title
        content: Card content
        icon: Emoji icon to display

    Example:
        >>> create_info_card("Tip", "Draw on the canvas to control the robot", "💡")
    """
    st.info(f"{icon} **{title}**: {content}")


def create_warning_card(title: str, content: str) -> None:
    """
    Create a warning card.

    Args:
        title: Warning title
        content: Warning message

    Example:
        >>> create_warning_card("Caution", "Make sure the robot workspace is clear")
    """
    st.warning(f"⚠️ **{title}**: {content}")


def create_columns_layout(ratios: list) -> tuple:
    """
    Create a column layout with specified ratios.

    Args:
        ratios: List of column width ratios

    Returns:
        Tuple of column objects

    Example:
        >>> col1, col2 = create_columns_layout([0.3, 0.7])
    """
    return st.columns(ratios)


def display_robot_status(robot_arm) -> None:
    """
    Display robot arm status information.

    Args:
        robot_arm: RobotArmController instance

    Example:
        >>> display_robot_status(st.session_state.robot_arm)
    """
    if robot_arm.is_port_available():
        st.success(f"✅ Robot Arm Connected (Port: {robot_arm.port})")
    else:
        st.error("❌ Robot Arm Not Detected")
        st.info("Please connect the robot arm via USB and refresh the page.")


def display_camera_status(camera_manager) -> None:
    """
    Display camera system status.

    Args:
        camera_manager: CameraManager instance

    Example:
        >>> display_camera_status(st.session_state.camera_manager)
    """
    active_cameras = camera_manager.get_active_cameras()
    if active_cameras:
        st.success(f"✅ {len(active_cameras)} Camera(s) Active: {active_cameras}")
    else:
        st.error("❌ No Cameras Detected")


def create_control_panel(title: str) -> None:
    """
    Create a standardized control panel header.

    Args:
        title: Control panel title

    Example:
        >>> create_control_panel("Motor Controls")
    """
    st.markdown(f"## {title}")
    st.markdown("---")


def create_expandable_section(title: str, expanded: bool = False):
    """
    Create an expandable section using Streamlit expander.

    Args:
        title: Section title
        expanded: Whether section is expanded by default

    Returns:
        Streamlit expander object

    Example:
        >>> with create_expandable_section("Advanced Settings"):
        ...     st.slider("Speed", 0, 100)
    """
    return st.expander(title, expanded=expanded)


def show_loading_spinner(message: str = "Loading..."):
    """
    Show a loading spinner with custom message.

    Args:
        message: Loading message to display

    Returns:
        Streamlit spinner context manager

    Example:
        >>> with show_loading_spinner("Processing image..."):
        ...     process_image()
    """
    return st.spinner(message)


# Color scheme constants
class Colors:
    """Color palette for consistent UI styling."""
    PRIMARY = "#FF4B4B"
    SECONDARY = "#0068C9"
    SUCCESS = "#00C851"
    WARNING = "#FFB300"
    ERROR = "#FF4444"
    INFO = "#33B5E5"
    BACKGROUND = "#FFFFFF"
    TEXT = "#262730"


# Icon constants
class Icons:
    """Common emoji icons for UI elements."""
    ROBOT = "🤖"
    CAMERA = "📷"
    DRAW = "✏️"
    HAND = "✋"
    CHECK = "✅"
    CROSS = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    SETTINGS = "⚙️"
    PLAY = "▶️"
    STOP = "⏹️"
    REFRESH = "🔄"

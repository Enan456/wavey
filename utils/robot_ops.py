import json
import serial
from serial.tools import list_ports
import streamlit as st

class RobotArmController:
    """
    Encapsulates the logic for detecting and controlling the robotic arm via serial port.
    """

    def __init__(self, baudrate=115200, timeout=1):
        self.baudrate = baudrate
        self.timeout = timeout
        self.port = self._detect_robot_arm_port()

    def _detect_robot_arm_port(self):
        """
        Detects the first available USB/TTY port that might be the robotic arm.
        Returns the port device name if found, else None.
        """
        for port in list_ports.comports():
            if "usb" in port.device.lower() or "tty" in port.device.lower():
                return port.device
        return None

    def is_port_available(self):
        return self.port is not None

    def send_command(self, command):
        """
        Send a JSON command to the robotic arm via the detected serial port.
        """
        if not self.is_port_available():
            st.error("No robotic arm port detected.")
            return

        try:
            with serial.Serial(self.port, baudrate=self.baudrate, timeout=self.timeout) as ser:
                ser.write((json.dumps(command) + "\n").encode())
            st.success(f"Command sent: {command}")
        except Exception as e:
            st.error(f"Failed to send command: {e}")

    # ------------------------
    # High-level control APIs
    # ------------------------

    def set_motor_angles(self, motor_angles):
        """
        Sends angles for each motor (1-4) in degrees.
        """
        command = {"T": 999, "angles": motor_angles}
        self.send_command(command)

    def open_hand(self, open_angle=3.14, speed=0.5, acc=10):
        """
        Command to open the gripper to a specific angle (radians).
        """
        command = {"T": 106, "cmd": open_angle, "spd": speed, "acc": acc}
        self.send_command(command)

    def close_hand(self, close_angle=1.2, speed=0.5, acc=10):
        """
        Command to close the gripper to a specific angle (radians).
        """
        command = {"T": 106, "cmd": close_angle, "spd": speed, "acc": acc}
        self.send_command(command)

    def point_to_angle(self, joint=1, angle=90, speed=10, acc=10):
        """
        Moves a given joint to a specific angle (in degrees).
        """
        command = {"T": 121, "joint": joint, "angle": angle, "spd": speed, "acc": acc}
        self.send_command(command)

    def pick_up(self, x=200, y=0, z=50, t=1.57, speed=0.5):
        """
        Move the end-effector to the specified (x, y, z) with orientation 't' and speed 'spd'.
        """
        command = {"T": 104, "x": x, "y": y, "z": z, "t": t, "spd": speed}
        self.send_command(command)

    def draw_on_table(self, start_x=100, start_y=100, end_x=200, end_y=200, z=50, t=1.57, speed=0.5):
        """
        Example of a multi-step action: move to start, then move to end.
        """
        command_start = {
            "T": 104,
            "x": start_x,
            "y": start_y,
            "z": z,
            "t": t,
            "spd": speed
        }
        command_end = {
            "T": 104,
            "x": end_x,
            "y": end_y,
            "z": z,
            "t": t,
            "spd": speed
        }
        self.send_command(command_start)
        self.send_command(command_end)


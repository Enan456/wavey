import json
import serial
from serial.tools import list_ports
import time
from typing import Dict, Optional, Union


class RobotArmController:
    """
    Encapsulates the logic for detecting and controlling the robotic arm via serial port.
    """

    def __init__(self, baudrate: int = 115200, timeout: float = 1) -> None:
        self.baudrate: int = baudrate
        self.timeout: float = timeout
        self.port: Optional[str] = self._detect_robot_arm_port()

    def _detect_robot_arm_port(self) -> Optional[str]:
        """
        Detects the first available USB/TTY port that might be the robotic arm.
        Returns the port device name if found, else None.
        """
        for port in list_ports.comports():
            if "usb" in port.device.lower() or "tty" in port.device.lower():
                return port.device
        return None

    def is_port_available(self) -> bool:
        return self.port is not None

    def send_command(self, command: Dict) -> None:
        """
        Send a JSON command to the robotic arm via the detected serial port.
        """
        if not self.is_port_available():
            print("Warning: No robotic arm port detected.")
            return

        try:
            with serial.Serial(self.port, baudrate=self.baudrate, timeout=self.timeout) as ser:
                ser.write((json.dumps(command) + "\n").encode())
            #st.success(f"Command sent: {command}")
        except Exception as e:
            #st.error(f"Failed to send command: {e}")
            print(f"Failed to send command: {e}")

    # ------------------------
    # High-level control APIs
    # ------------------------

    def set_motor_angles(self, motor_angles: Dict[int, Union[int, float]]) -> None:
        """
        Sends angles for each motor (1-4) in degrees.
        """
        command = {"T": 999, "angles": motor_angles}
        self.send_command(command)

    def open_hand(self, open_angle: float = 3.14, speed: float = 0.5, acc: float = 10) -> None:
        """
        Command to open the gripper to a specific angle (radians).
        """
        command = {"T": 106, "cmd": open_angle, "spd": speed, "acc": acc}
        self.send_command(command)

    def close_hand(self, close_angle: float = 1.2, speed: float = 0.5, acc: float = 10) -> None:
        """
        Command to close the gripper to a specific angle (radians).
        """
        command = {"T": 106, "cmd": close_angle, "spd": speed, "acc": acc}
        self.send_command(command)

    def point_to_angle(self, joint: int = 1, angle: float = 90, speed: float = 10, acc: float = 10) -> None:
        """
        Moves a given joint to a specific angle (in degrees).
        """
        command = {"T": 121, "joint": joint, "angle": angle, "spd": speed, "acc": acc}
        self.send_command(command)

    def pick_up(self, x: float = 200, y: float = 0, z: float = 50, t: float = 1.57, speed: float = 0.5) -> None:
        """
        Move the end-effector to the specified (x, y, z) with orientation 't' and speed 'spd'.
        """
        command = {"T": 104, "x": x, "y": y, "z": z, "t": t, "spd": speed}
        self.send_command(command)

    def draw_on_table(self, start_x: float = 100, start_y: float = 100, end_x: float = 200, end_y: float = 200, z: float = 50, t: float = 1.57, speed: float = 0.5) -> None:
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

#run test if this file is run
if __name__ == "__main__":
    robot_arm = RobotArmController()
    print(robot_arm.is_port_available())
    robot_arm.set_motor_angles({1: 90, 2: 0, 3: 0, 4: 0})
    time.sleep(4)
    robot_arm.open_hand()
    time.sleep(2)
    robot_arm.close_hand()
    time.sleep(2)
    robot_arm.point_to_angle()
    time.sleep(2)
    robot_arm.pick_up()
    time.sleep(2)
    robot_arm.draw_on_table()
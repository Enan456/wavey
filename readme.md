messy working directory for waveshare robot code

streamlit run dashboard.py

streamlit run draw_dashboard.py


## Files

- `dashboard.py`: Main Streamlit application for controlling the robotic arm and displaying dual camera feeds with YOLO object detection.
- `draw_dashboard.py`: Streamlit application for drawing on a canvas and sending drawing instructions to the robotic arm.
- `requirements.txt`: List of Python dependencies required for the project.
- `utils/robot_ops.py`: Contains the `RobotArmController` class for controlling the robotic arm.
- `utils/video_processing.py`: Contains the `CameraManager` and `YOLOModel` classes for managing camera feeds and running YOLO object detection.
- `yolo11n.pt` and `yolov8n.pt`: YOLO model weights files.

## Installation

1. Clone the repository:
    ```sh
    git clone <repository_url>
    cd <repository_directory>
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

### Running the Dashboards

1. To run the main dashboard:
    ```sh
    streamlit run dashboard.py
    ```

2. To run the drawing dashboard:
    ```sh
    streamlit run draw_dashboard.py
    ```

## Robot Arm Control

The [RobotArmController](http://_vscodecontentref_/9) class in [robot_ops.py](http://_vscodecontentref_/10) provides methods to control the robotic arm, such as setting motor angles, opening/closing the hand, and moving to specific coordinates.

## Camera and YOLO Integration

The [CameraManager](http://_vscodecontentref_/11) and [YOLOModel](http://_vscodecontentref_/12) classes in [video_processing.py](http://_vscodecontentref_/13) handle camera feeds and YOLO object detection. The [get_annotated_frame](http://_vscodecontentref_/14) function retrieves frames from the camera and annotates them with YOLO detections.

## License

This project is licensed under the MIT License.
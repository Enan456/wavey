import cv2
import streamlit as st
from PIL import Image

# YOLO from ultralytics
from ultralytics import YOLO

class CameraManager:
    """
    Manages camera discovery, opening, and retrieving frames.
    """

    def __init__(self):
        self.cameras = self._list_active_cameras()
        self.caps = {}  # store cv2.VideoCapture objects

    def _list_active_cameras(self, max_test=10):
        """
        Check up to `max_test` indices, return those that are active.
        """
        active = []
        for i in range(max_test):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                active.append(i)
                cap.release()
        return active

    def open_capture(self, camera_index):
        """
        Open a VideoCapture for a given camera index.
        """
        if camera_index not in self.caps:
            cap = cv2.VideoCapture(camera_index)
            self.caps[camera_index] = cap

    def get_frame(self, camera_index):
        """
        Return the latest frame from the specified camera index (BGR format).
        If the camera is not open or fails to read, return None.
        """
        cap = self.caps.get(camera_index, None)
        if not cap or not cap.isOpened():
            return None
        ret, frame_bgr = cap.read()
        return frame_bgr if ret else None

class YOLOModel:
    """
    Loads a YOLO model (e.g. YOLOv8) and provides an inference method.
    """

    def __init__(self, model_path="yolov8n.pt", device='cpu', score_thr=0.3):
        """
        :param model_path: Path to your YOLOv8 model weights (trained on COCO, or any).
        :param device: 'cpu' or 'cuda' for GPU. (e.g. "cuda" or "cuda:0")
        :param score_thr: Confidence threshold for filtering predictions.
        """
        self.model = YOLO(model_path)
        self.score_thr = score_thr

    def run_inference(self, bgr_image):
        """
        Run inference on a BGR image, return the annotated BGR image.
        """
        results = self.model.track(bgr_image, stream=True)
        for result in results:
            classes_names = result.names
            for box in result.boxes:
                if box.conf[0] > self.score_thr:
                    [x1, y1, x2, y2] = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    cls = int(box.cls[0])
                    class_name = classes_names[cls]
                    colour = self.get_colours(cls)
                    cv2.rectangle(bgr_image, (x1, y1), (x2, y2), colour, 2)
                    cv2.putText(bgr_image, f'{class_name} {box.conf[0]:.2f}', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, colour, 2)
        return bgr_image

    def get_colours(self, cls_num):
        base_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        color_index = cls_num % len(base_colors)
        increments = [(1, -2, 1), (-2, 1, -1), (1, -1, 2)]
        color = [base_colors[color_index][i] + increments[color_index][i] * (cls_num // len(base_colors)) % 256 for i in range(3)]
        return tuple(color)

def get_annotated_frame(camera_idx, camera_manager, detection_model):
    """
    Helper function that reads a frame from `camera_manager`, runs detection using `detection_model`,
    and returns a PIL Image (RGB) with bounding box annotations.
    """
    frame = camera_manager.get_frame(camera_idx)
    if frame is None:
        return None
    annotated_frame = detection_model.run_inference(frame)
    return Image.fromarray(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB))

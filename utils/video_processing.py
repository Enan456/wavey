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

    def __init__(self, model_path="yolov8n.pt", device="cuda", score_thr=0.3):
        """
        :param model_path: Path to your YOLOv8 model weights (trained on COCO, or any).
        :param device: 'cpu' or 'cuda' for GPU. (e.g. "cuda" or "cuda:0")
        :param score_thr: Confidence threshold for filtering predictions.
        """
        self.model = YOLO(model_path)
        self.model.to(device)
        self.score_thr = score_thr

    def run_inference(self, bgr_image):
        """
        Run inference on a BGR image, return the annotated BGR image.
        """
        # Perform detection; results is a list of 'ultralytics.yolo.engine.results.Results'
        results = self.model.predict(source=bgr_image, conf=self.score_thr)
        # results[0].plot() returns an RGB numpy array
        annotated_rgb = results[0].plot()
        # Convert back to BGR for consistency
        annotated_bgr = cv2.cvtColor(annotated_rgb, cv2.COLOR_RGB2BGR)
        return annotated_bgr

def get_annotated_frame(camera_idx, camera_manager, detection_model):
    """
    Helper function that reads a frame from `camera_manager`, runs detection using `detection_model`,
    and returns a PIL Image (RGB) with bounding box annotations.
    Uses Streamlit session_state to store fallback frame if needed.
    """
    fallback_key = f"frame_{camera_idx}"
    fallback_frame = st.session_state.get(fallback_key, None)

    frame_bgr = camera_manager.get_frame(camera_idx)
    if frame_bgr is None:
        # Fallback to last known frame if read fails
        return fallback_frame

    # Run YOLO detection
    annotated_bgr = detection_model.run_inference(frame_bgr)

    # Convert to RGB for display
    annotated_rgb = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(annotated_rgb)

    # Store in session_state
    st.session_state[fallback_key] = pil_img
    return pil_img

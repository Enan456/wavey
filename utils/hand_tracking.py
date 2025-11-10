"""
Hand tracking utilities using YOLO models.
Supports both YOLOv8 pose estimation and custom hand detection models.
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional
from PIL import Image
from ultralytics import YOLO
import config


class HandTracker:
    """
    Hand tracking using YOLO models.
    Supports pose estimation (YOLOv8-pose) for hand keypoint detection.
    """

    def __init__(
        self,
        model_path: str = "yolov8n-pose.pt",
        device: str = config.YOLO_DEVICE,
        score_thr: float = config.HAND_SCORE_THRESHOLD
    ) -> None:
        """
        Initialize hand tracker with YOLO pose model.

        Args:
            model_path: Path to YOLO pose model (e.g., 'yolov8n-pose.pt')
            device: 'cpu' or 'cuda'
            score_thr: Confidence threshold for detections
        """
        self.model: YOLO = YOLO(model_path)
        self.device: str = device
        self.score_thr: float = score_thr

        # Hand keypoint indices in COCO pose format
        # COCO format: 0-nose, 1-left_eye, 2-right_eye, 3-left_ear, 4-right_ear,
        # 5-left_shoulder, 6-right_shoulder, 7-left_elbow, 8-right_elbow,
        # 9-left_wrist, 10-right_wrist, 11-left_hip, 12-right_hip,
        # 13-left_knee, 14-right_knee, 15-left_ankle, 16-right_ankle
        self.LEFT_WRIST = 9
        self.RIGHT_WRIST = 10
        self.LEFT_ELBOW = 7
        self.RIGHT_ELBOW = 8

    def detect_hands(self, bgr_image: np.ndarray) -> Tuple[List[Dict], np.ndarray]:
        """
        Detect hands in image using YOLO pose estimation.

        Args:
            bgr_image: Input image in BGR format

        Returns:
            Tuple of (hand_detections, annotated_image)
            hand_detections: List of dicts with 'position', 'side', 'confidence'
            annotated_image: BGR image with hand positions drawn
        """
        results = self.model(bgr_image, verbose=False)
        hand_detections: List[Dict] = []

        for result in results:
            if result.keypoints is None:
                continue

            keypoints = result.keypoints.data  # Shape: (num_people, num_keypoints, 3)

            for person_kpts in keypoints:
                # Check if keypoints array has enough elements
                if len(person_kpts) < 17:  # COCO pose has 17 keypoints
                    continue

                # Extract wrist keypoints (x, y, confidence)
                left_wrist = person_kpts[self.LEFT_WRIST]
                right_wrist = person_kpts[self.RIGHT_WRIST]

                # Check left hand
                if left_wrist[2] > self.score_thr:  # confidence check
                    x, y = int(left_wrist[0]), int(left_wrist[1])
                    hand_detections.append({
                        'position': (x, y),
                        'side': 'left',
                        'confidence': float(left_wrist[2]),
                        'keypoint': 'wrist'
                    })
                    # Draw on image
                    cv2.circle(bgr_image, (x, y), 10, (0, 255, 0), -1)
                    cv2.putText(bgr_image, f'L Hand {left_wrist[2]:.2f}',
                              (x + 15, y), cv2.FONT_HERSHEY_SIMPLEX,
                              0.6, (0, 255, 0), 2)

                # Check right hand
                if right_wrist[2] > self.score_thr:
                    x, y = int(right_wrist[0]), int(right_wrist[1])
                    hand_detections.append({
                        'position': (x, y),
                        'side': 'right',
                        'confidence': float(right_wrist[2]),
                        'keypoint': 'wrist'
                    })
                    # Draw on image
                    cv2.circle(bgr_image, (x, y), 10, (255, 0, 0), -1)
                    cv2.putText(bgr_image, f'R Hand {right_wrist[2]:.2f}',
                              (x + 15, y), cv2.FONT_HERSHEY_SIMPLEX,
                              0.6, (255, 0, 0), 2)

        return hand_detections, bgr_image

    def detect_hand_gestures(self, bgr_image: np.ndarray) -> Tuple[List[Dict], np.ndarray]:
        """
        Detect hand gestures by analyzing wrist and elbow positions.

        Args:
            bgr_image: Input image in BGR format

        Returns:
            Tuple of (gesture_detections, annotated_image)
        """
        results = self.model(bgr_image, verbose=False)
        gesture_detections: List[Dict] = []

        for result in results:
            if result.keypoints is None:
                continue

            keypoints = result.keypoints.data

            for person_kpts in keypoints:
                # Check if keypoints array has enough elements
                if len(person_kpts) < 17:  # COCO pose has 17 keypoints
                    continue

                left_wrist = person_kpts[self.LEFT_WRIST]
                right_wrist = person_kpts[self.RIGHT_WRIST]
                left_elbow = person_kpts[self.LEFT_ELBOW]
                right_elbow = person_kpts[self.RIGHT_ELBOW]

                # Analyze left hand gesture
                if left_wrist[2] > self.score_thr and left_elbow[2] > self.score_thr:
                    gesture = self._classify_gesture(left_wrist, left_elbow)
                    if gesture:
                        gesture_detections.append({
                            'side': 'left',
                            'gesture': gesture,
                            'position': (int(left_wrist[0]), int(left_wrist[1]))
                        })
                        # Draw gesture on image
                        cv2.putText(bgr_image, f'L: {gesture}',
                                  (int(left_wrist[0]), int(left_wrist[1]) - 20),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                # Analyze right hand gesture
                if right_wrist[2] > self.score_thr and right_elbow[2] > self.score_thr:
                    gesture = self._classify_gesture(right_wrist, right_elbow)
                    if gesture:
                        gesture_detections.append({
                            'side': 'right',
                            'gesture': gesture,
                            'position': (int(right_wrist[0]), int(right_wrist[1]))
                        })
                        # Draw gesture on image
                        cv2.putText(bgr_image, f'R: {gesture}',
                                  (int(right_wrist[0]), int(right_wrist[1]) - 20),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        return gesture_detections, bgr_image

    def _classify_gesture(self, wrist: np.ndarray, elbow: np.ndarray) -> str:
        """
        Classify hand gesture based on wrist and elbow positions.

        Args:
            wrist: [x, y, confidence] of wrist
            elbow: [x, y, confidence] of elbow

        Returns:
            Gesture name ('raised', 'lowered', 'forward', etc.)
        """
        wrist_y = wrist[1]
        elbow_y = elbow[1]

        # Simple gesture classification based on vertical position
        if wrist_y < elbow_y - 50:
            return "raised"
        elif wrist_y > elbow_y + 50:
            return "lowered"
        else:
            return "extended"

    def track_hand_movement(
        self,
        bgr_image: np.ndarray,
        prev_positions: Optional[Dict[str, Tuple[int, int]]] = None
    ) -> Tuple[List[Dict], Dict[str, Tuple[int, int]], np.ndarray]:
        """
        Track hand movement between frames.

        Args:
            bgr_image: Current frame in BGR format
            prev_positions: Previous hand positions {'left': (x,y), 'right': (x,y)}

        Returns:
            Tuple of (movements, current_positions, annotated_image)
            movements: List of dicts with 'side', 'direction', 'distance'
        """
        hand_detections, annotated_image = self.detect_hands(bgr_image)

        current_positions: Dict[str, Tuple[int, int]] = {}
        movements: List[Dict] = []

        for detection in hand_detections:
            side = detection['side']
            position = detection['position']
            current_positions[side] = position

            # Calculate movement if we have previous position
            if prev_positions and side in prev_positions:
                prev_pos = prev_positions[side]
                dx = position[0] - prev_pos[0]
                dy = position[1] - prev_pos[1]
                distance = np.sqrt(dx**2 + dy**2)

                # Determine direction
                direction = "stationary"
                if distance > 10:  # threshold for movement
                    if abs(dx) > abs(dy):
                        direction = "right" if dx > 0 else "left"
                    else:
                        direction = "down" if dy > 0 else "up"

                movements.append({
                    'side': side,
                    'direction': direction,
                    'distance': float(distance),
                    'delta': (dx, dy)
                })

                # Draw movement arrow
                if distance > 10:
                    cv2.arrowedLine(
                        annotated_image,
                        prev_pos,
                        position,
                        (0, 255, 255),
                        3,
                        tipLength=0.3
                    )

        return movements, current_positions, annotated_image


def get_hand_tracked_frame(
    camera_idx: int,
    camera_manager,
    hand_tracker: HandTracker,
    track_movement: bool = False,
    prev_positions: Optional[Dict] = None
) -> Tuple[Optional[Image.Image], Optional[List[Dict]], Optional[Dict]]:
    """
    Get frame with hand tracking annotations.

    Args:
        camera_idx: Camera index
        camera_manager: CameraManager instance
        hand_tracker: HandTracker instance
        track_movement: Whether to track hand movement
        prev_positions: Previous hand positions for movement tracking

    Returns:
        Tuple of (annotated_image, detections/movements, current_positions)
    """
    frame = camera_manager.get_frame(camera_idx)
    if frame is None:
        return None, None, None

    if track_movement and prev_positions is not None:
        movements, positions, annotated = hand_tracker.track_hand_movement(frame, prev_positions)
        rgb_image = Image.fromarray(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB))
        return rgb_image, movements, positions
    else:
        detections, annotated = hand_tracker.detect_hands(frame)
        rgb_image = Image.fromarray(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB))
        return rgb_image, detections, None

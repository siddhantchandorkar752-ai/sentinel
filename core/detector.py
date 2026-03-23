import cv2
import numpy as np
import mediapipe as mp
from ultralytics import YOLO

class DetectionEngine:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        try:
            self.yolo = YOLO('yolov8n-face.pt')
        except:
            self.yolo = None # Fallback

    def process_frame(self, frame: np.ndarray):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Bounding box det
        bbox = None
        if self.yolo:
            results = self.yolo(frame, verbose=False)
            if len(results[0].boxes) > 0:
                box = results[0].boxes[0].xyxy[0].cpu().numpy()
                bbox = (int(box[0]), int(box[1]), int(box[2]), int(box[3]))
        
        # Landmarks
        results = self.mp_face_mesh.process(rgb_frame)
        landmarks = None
        if results.multi_face_landmarks:
            h, w, _ = frame.shape
            landmarks = []
            for lm in results.multi_face_landmarks[0].landmark:
                landmarks.append([lm.x * w, lm.y * h])
            landmarks = np.array(landmarks)
            
        return bbox, landmarks

import cv2
import numpy as np
import mediapipe as mp
class DetectionEngine:
    def __init__(self):
        # Using pure MediaPipe to eliminate YOLO inference latency completely
        self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
    def process_frame(self, frame: np.ndarray):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Landmarks extraction (runs internal fast BlazeFace detector)
        results = self.mp_face_mesh.process(rgb_frame)
        landmarks = None
        bbox = None
        
        h, w, _ = frame.shape
        if results.multi_face_landmarks:
            landmarks = []
            # Optimized 1D extraction
            for lm in results.multi_face_landmarks[0].landmark:
                landmarks.append([lm.x * w, lm.y * h])
            landmarks = np.array(landmarks)
            
            # Calculate robust bounding box directly from Mesh to fully replace YOLO
            x_min = int(np.min(landmarks[:, 0]))
            y_min = int(np.min(landmarks[:, 1]))
            x_max = int(np.max(landmarks[:, 0]))
            y_max = int(np.max(landmarks[:, 1]))
            
            # Add padding
            padding_x = max(10, int((x_max - x_min) * 0.15))
            padding_y = max(10, int((y_max - y_min) * 0.15))
            
            bbox = (max(0, x_min - padding_x), 
                    max(0, y_min - int(padding_y*1.5)), 
                    min(w, x_max + padding_x), 
                    min(h, y_max + padding_y))
            
        return bbox, landmarks

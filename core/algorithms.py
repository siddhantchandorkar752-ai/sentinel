import numpy as np
import cv2

class KalmanFilter1D:
    def __init__(self, process_noise=1e-5, measurement_noise=1e-2):
        self.q = process_noise
        self.r = measurement_noise
        self.x = 0.0
        self.p = 1.0

    def update(self, measurement):
        p_pred = self.p + self.q
        k = p_pred / (p_pred + self.r)
        self.x = self.x + k * (measurement - self.x)
        self.p = (1 - k) * p_pred
        return self.x

def calculate_ear(eye_landmarks) -> float:
    # 33 landmarks per eye; simplifying to standard 6 points for EAR
    # For mediapipe, mapping standard 6 points: (left eye example)
    p2_p6 = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
    p3_p5 = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
    p1_p4 = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
    if p1_p4 == 0: return 0.0
    return (p2_p6 + p3_p5) / (2.0 * p1_p4)

def calculate_mar(mouth_landmarks) -> float:
    vertical_dist = np.linalg.norm(mouth_landmarks[3] - mouth_landmarks[9])
    horizontal_dist = np.linalg.norm(mouth_landmarks[0] - mouth_landmarks[6])
    if horizontal_dist == 0: return 0.0
    return vertical_dist / horizontal_dist

def solve_head_pose(face_landmarks, frame_shape):
    h, w, c = frame_shape
    focal_length = w
    cam_matrix = np.array([[focal_length, 0, w / 2],
                           [0, focal_length, h / 2],
                           [0, 0, 1]], dtype=np.float64)
    dist_coeffs = np.zeros((4, 1), dtype=np.float64)
    model_points = np.array([
        (0.0, 0.0, 0.0),             # Nose tip
        (0.0, -330.0, -65.0),        # Chin
        (-225.0, 170.0, -135.0),     # Left eye left corner
        (225.0, 170.0, -135.0),      # Right eye right corner
        (-150.0, -150.0, -125.0),    # Left Mouth corner
        (150.0, -150.0, -125.0)      # Right mouth corner
    ])
    
    # Simple mapping for illustration
    image_points = np.array([
        face_landmarks[4], face_landmarks[152], face_landmarks[33],
        face_landmarks[263], face_landmarks[61], face_landmarks[291]
    ], dtype=np.float64)
    
    success, rotation_vec, translation_vec = cv2.solvePnP(
        model_points, image_points, cam_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)
    
    rmat, _ = cv2.Rodrigues(rotation_vec)
    angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
    pitch, yaw, roll = angles[0], angles[1], angles[2]
    return pitch, yaw, roll

class PERCLOSCalculator:
    def __init__(self, history_size=1800): # 60 secs at 30fps
        self.history = []
        self.size = history_size
    
    def update(self, is_closed: bool) -> float:
        self.history.append(is_closed)
        if len(self.history) > self.size:
            self.history.pop(0)
        return sum(self.history) / len(self.history)

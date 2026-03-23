import gradio as gr
import cv2
import numpy as np
from core.detector import DetectionEngine
from core.algorithms import calculate_ear, calculate_mar, solve_head_pose, KalmanFilter1D
from core.tracker import DrowsinessTracker, State
from core.alerts import AlertSystem
import plotly.graph_objects as go
from collections import deque
detector = DetectionEngine()
tracker = DrowsinessTracker()
alerts = AlertSystem()
ear_filter = KalmanFilter1D()
mar_filter = KalmanFilter1D()
ear_history = deque(maxlen=30)
timestamps = deque(maxlen=30)
frame_count = 0
def process_frame(frame):
    global frame_count
    if frame is None: return None, go.Figure(), "0.00", "0.00", "N/A", "N/A", "0%"
    
    bbox, landmarks = detector.process_frame(frame)
    ear, mar, p, y, r = 0.0, 0.0, 0.0, 0.0, 0.0
    state = State.ALERT
    perclos = 0.0
    
    if landmarks is not None:
        left_eye = landmarks[[33, 160, 158, 133, 153, 144]]
        right_eye = landmarks[[362, 385, 387, 263, 373, 380]]
        mouth = landmarks[[78, 81, 13, 311, 308, 402, 14, 178, 61, 291]]
        
        ear_l = calculate_ear(left_eye)
        ear_r = calculate_ear(right_eye)
        ear = (ear_l + ear_r) / 2.0  # Removed Kalman lag for INSTANT detection!
        mar = mar_filter.update(calculate_mar(mouth))
        p, y, r = solve_head_pose(landmarks, frame.shape)
        
        state, perclos = tracker.update(ear, 0.25)
        
        # Continuously update the single unified alert system
        alerts.update_state(state)
            
        # Draw explicit eye tracking dots so user can SEE the tracking
        for pt in left_eye:
            cv2.circle(frame, (int(pt[0]), int(pt[1])), 2, (0, 255, 255), -1)
        for pt in right_eye:
            cv2.circle(frame, (int(pt[0]), int(pt[1])), 2, (0, 255, 255), -1)
        # UI overlays
        color = (0, 255, 0)
        if state == State.DROWSY_WARNING: 
            color = (0, 255, 255)
            cv2.putText(frame, "WARNING!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)
        elif state == State.DROWSY_CRITICAL: 
            color = (0, 0, 255)
            cv2.putText(frame, "CRITICAL: WAKE UP!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)
        elif state == State.MICROSLEEP: 
            color = (255, 0, 255)
            cv2.putText(frame, "MICROSLEEP: VEHICLE STOPPING!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)
        
        if bbox:
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            
    ear_history.append(ear)
    timestamps.append(frame_count)
    frame_count += 1
    
    fig = go.Figure(data=go.Scatter(x=list(timestamps), y=list(ear_history), mode='lines'))
    fig.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0), title="EAR Trend")
    
    return frame, fig, f"{ear:.2f}", f"{mar:.2f}", f"P:{p:.1f} Y:{y:.1f} R:{r:.1f}", state.value, f"{perclos*100:.1f}%"
with gr.Blocks(theme=gr.themes.Monochrome()) as demo:
    gr.Markdown("# SENTINEL v2.0 - Driver Monitoring")
    with gr.Row():
        with gr.Column(scale=2):
            video_input = gr.Image(sources=["webcam"], streaming=True)
            annotated_video = gr.Image()
            video_input.stream(process_frame, [video_input], [
                annotated_video, 
                gr.Plot(label="EAR Plot"),
                gr.Textbox(label="EAR"), 
                gr.Textbox(label="MAR"), 
                gr.Textbox(label="Head Pose"), 
                gr.Textbox(label="State"), 
                gr.Textbox(label="PERCLOS")
            ])
            
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
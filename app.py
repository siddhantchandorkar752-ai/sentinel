import gradio as gr
import cv2
import numpy as np
import plotly.graph_objects as go
from collections import deque

# Lazy imports (prevents crash if missing heavy deps)
try:
    from core.detector import DetectionEngine
    from core.algorithms import calculate_ear, calculate_mar, solve_head_pose, KalmanFilter1D
    from core.tracker import DrowsinessTracker, State
    from core.alerts import AlertSystem
    
    detector = DetectionEngine()
    tracker = DrowsinessTracker()
    alerts = AlertSystem()
    mar_filter = KalmanFilter1D()
    
    MODEL_LOADED = True
except Exception as e:
    print("Model load error:", e)
    MODEL_LOADED = False

ear_history = deque(maxlen=30)
timestamps = deque(maxlen=30)
frame_count = 0


def process_frame(frame):
    global frame_count
    
    if frame is None:
        return None, go.Figure(), "0", "0", "N/A", "N/A", "0%"
    
    if not MODEL_LOADED:
        return frame, go.Figure(), "0", "0", "Model Error", "N/A", "0%"
    
    bbox, landmarks = detector.process_frame(frame)
    
    ear, mar, p, y, r = 0, 0, 0, 0, 0
    state = State.ALERT
    perclos = 0
    
    if landmarks is not None:
        left_eye = landmarks[[33, 160, 158, 133, 153, 144]]
        right_eye = landmarks[[362, 385, 387, 263, 373, 380]]
        mouth = landmarks[[78, 81, 13, 311, 308, 402, 14, 178, 61, 291]]
        
        ear = (calculate_ear(left_eye) + calculate_ear(right_eye)) / 2
        mar = mar_filter.update(calculate_mar(mouth))
        p, y, r = solve_head_pose(landmarks, frame.shape)
        
        state, perclos = tracker.update(ear, 0.25)
        alerts.update_state(state)
        
        color = (0, 255, 0)
        if state != State.ALERT:
            color = (0, 0, 255)
        
        if bbox:
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)

    ear_history.append(ear)
    timestamps.append(frame_count)
    frame_count += 1

    fig = go.Figure(data=go.Scatter(
        x=list(timestamps),
        y=list(ear_history),
        mode='lines'
    ))

    fig.update_layout(height=200)

    return frame, fig, f"{ear:.2f}", f"{mar:.2f}", f"{p:.1f},{y:.1f},{r:.1f}", state.value, f"{perclos*100:.1f}%"


with gr.Blocks() as demo:
    gr.Markdown("# 🚗 SENTINEL v2.0 - Driver Monitoring")
    
    video_input = gr.Image(sources=["webcam"], streaming=True)
    output = [
        gr.Image(),
        gr.Plot(),
        gr.Textbox(label="EAR"),
        gr.Textbox(label="MAR"),
        gr.Textbox(label="Head Pose"),
        gr.Textbox(label="State"),
        gr.Textbox(label="PERCLOS")
    ]
    
    video_input.stream(process_frame, inputs=video_input, outputs=output)

if __name__ == "__main__":
    demo.launch()

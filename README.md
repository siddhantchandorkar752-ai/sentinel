# SENTINEL v2.0

Real-Time Driver Drowsiness & Distraction Detection System for production environments.

## Architecture Highlights
- **Multi-Modal Detection**: YOLOv8 + MediaPipe FaceMesh
- **Deep Learning**: MobileNetV3 (PyTorch -> ONNX Runtime)
- **Algorithms**: EAR, MAR, Head Pose (solvePnP), PERCLOS, Kalman Filtering
- **Analytics & API**: FastAPI + SQLite
- **UI**: Gradio 4.x
- **Containerization**: Docker with CUDA 11.8 support

## Quickstart
1. `copy .env.example .env` and update variables
2. `docker-compose up --build`
3. Access UI at `http://localhost:7860`
4. Access API Docs at `http://localhost:8000/docs`

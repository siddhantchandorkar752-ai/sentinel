import onnxruntime as ort
import numpy as np
import cv2

class EyeStateClassifier:
    def __init__(self, model_path="models/weights/mobilenetv3_eye.onnx"):
        self.session = None
        try:
            self.session = ort.InferenceSession(model_path, providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
            self.input_name = self.session.get_inputs()[0].name
        except Exception as e:
            print(f"ONNX Model not loaded, using purely EAR fallback: {e}")
            
    def predict(self, eye_roi: np.ndarray) -> float:
        if self.session is None: return 1.0 # default open
        
        img = cv2.resize(eye_roi, (224, 224))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype(np.float32) / 255.0
        img = np.transpose(img, (2, 0, 1))
        img = np.expand_dims(img, axis=0)
        
        preds = self.session.run(None, {self.input_name: img})[0]
        # output is probability of eye being open (0 to 1)
        return float(preds[0][0])

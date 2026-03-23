import torch
from models.train import get_model
import os

def export():
    model = get_model()
    try:
        model.load_state_dict(torch.load("models/weights/mobilenetv3_eye.pt"))
    except:
        pass
    model.eval()
    
    dummy_input = torch.randn(1, 3, 224, 224)
    onnx_path = "models/weights/mobilenetv3_eye.onnx"
    os.makedirs(os.path.dirname(onnx_path), exist_ok=True)
    
    torch.onnx.export(
        model, dummy_input, onnx_path,
        export_params=True, opset_version=11,
        do_constant_folding=True,
        input_names=['input'], output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )
    print(f"Exported to {onnx_path}")

if __name__ == "__main__":
    export()

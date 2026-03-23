import torch
import torchvision.models as models
import torch.nn as nn

def get_model():
    model = models.mobilenet_v3_small(pretrained=True)
    model.classifier[3] = nn.Linear(model.classifier[3].in_features, 1)
    return model

if __name__ == "__main__":
    print("Training script placeholder. Use standard PyTorch train loop on CEW dataset.")
    model = get_model()
    # Dummy save for export
    import os
    os.makedirs("models/weights", exist_ok=True)
    torch.save(model.state_dict(), "models/weights/mobilenetv3_eye.pt")

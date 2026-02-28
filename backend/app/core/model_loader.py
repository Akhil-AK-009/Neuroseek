# app/core/model_loader.py

import os
import torch
import torch.nn as nn
from torchvision import models
import joblib

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "ml_models")

# -----------------------------
# 🔹 HANDWRITING MODEL CLASS
# -----------------------------
class HandwritingClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = models.resnet18(pretrained=False)
        self.model.fc = nn.Sequential(
            nn.Linear(self.model.fc.in_features, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, 2)
        )

    def forward(self, x):
        return self.model(x)


# -----------------------------
# 🔹 SPEECH MODEL CLASS
# -----------------------------
class SpeechCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone = models.resnet18(pretrained=False)
        self.backbone.fc = nn.Sequential(
            nn.Linear(self.backbone.fc.in_features, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, 2)
        )

    def forward(self, x):
        return self.backbone(x)


# -----------------------------
# 🔹 GLOBAL MODEL REGISTRY
# -----------------------------
MODELS = {}


def load_models():
    print("🔄 Loading ML models...")

    # Handwriting Models
    spiral_model = HandwritingClassifier().to(DEVICE)
    spiral_path = os.path.join(MODEL_DIR, "spiral_model.pth")
    spiral_model.load_state_dict(torch.load(spiral_path, map_location=DEVICE))
    spiral_model.eval()

    wave_model = HandwritingClassifier().to(DEVICE)
    wave_path = os.path.join(MODEL_DIR, "wave_model.pth")
    wave_model.load_state_dict(torch.load(wave_path, map_location=DEVICE))
    wave_model.eval()

    # Speech Model
    speech_model = SpeechCNN().to(DEVICE)
    speech_path = os.path.join(MODEL_DIR, "speech_best_finetuned.pth")
    speech_model.load_state_dict(torch.load(speech_path, map_location=DEVICE))
    speech_model.eval()

    # Gait Model
    gait_model_path = os.path.join(MODEL_DIR, "gait_video_xgb_model.pkl")
    gait_scaler_path = os.path.join(MODEL_DIR, "gait_video_scaler_norm.pkl")
    gait_threshold_path = os.path.join(MODEL_DIR, "gait_video_threshold.pkl")

    gait_model = joblib.load(gait_model_path)
    gait_scaler = joblib.load(gait_scaler_path)
    gait_threshold = joblib.load(gait_threshold_path)

    MODELS["spiral"] = spiral_model
    MODELS["wave"] = wave_model
    MODELS["speech"] = speech_model
    MODELS["gait_model"] = gait_model
    MODELS["gait_scaler"] = gait_scaler
    MODELS["gait_threshold"] = gait_threshold

    print("✅ All models loaded successfully!")
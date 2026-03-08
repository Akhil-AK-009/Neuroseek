import os
import torch
import torch.nn as nn
from torchvision import models

MODELS = {}

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_DIR = os.path.join(BASE_DIR, "ml_models")


# ---------------------------------------------------
# Utility: Clean model prefixes
# ---------------------------------------------------
def clean_state_dict(state_dict):

    new_state_dict = {}

    for k, v in state_dict.items():

        if k.startswith("model."):
            k = k.replace("model.", "")

        if k.startswith("backbone."):
            k = k.replace("backbone.", "")

        new_state_dict[k] = v

    return new_state_dict


# ---------------------------------------------------
# Gait Model Architecture (from training code)
# ---------------------------------------------------
class GaitBinaryCNN(nn.Module):

    def __init__(self):

        super(GaitBinaryCNN, self).__init__()

        self.conv1 = nn.Conv1d(272, 128, kernel_size=5, padding=2)
        self.bn1 = nn.BatchNorm1d(128)

        self.conv2 = nn.Conv1d(128, 64, kernel_size=5, padding=2)
        self.bn2 = nn.BatchNorm1d(64)

        self.conv3 = nn.Conv1d(64, 32, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm1d(32)

        self.pool = nn.AdaptiveAvgPool1d(1)

        self.fc = nn.Linear(32, 2)

    def forward(self, x):

        x = x.permute(0, 2, 1)

        x = torch.relu(self.bn1(self.conv1(x)))
        x = torch.relu(self.bn2(self.conv2(x)))
        x = torch.relu(self.bn3(self.conv3(x)))

        x = self.pool(x).squeeze(-1)

        x = self.fc(x)

        return x


# ---------------------------------------------------
# Load All Models
# ---------------------------------------------------
def load_models():

    print("🔄 Loading ML models...")

    # ====================================
    # Spiral Handwriting Model
    # ====================================

    spiral_path = os.path.join(MODEL_DIR, "spiral_model.pth")

    spiral_model = models.resnet18(weights=None)

    spiral_model.fc = nn.Sequential(
        nn.Linear(spiral_model.fc.in_features, 256),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(256, 2)
    )

    spiral_weights = torch.load(spiral_path, map_location=DEVICE)
    spiral_weights = clean_state_dict(spiral_weights)

    spiral_model.load_state_dict(spiral_weights)

    spiral_model.to(DEVICE)
    spiral_model.eval()

    MODELS["spiral"] = spiral_model

    print("✓ Spiral model loaded")


    # ====================================
    # Wave Handwriting Model
    # ====================================

    wave_path = os.path.join(MODEL_DIR, "wave_model.pth")

    wave_model = models.resnet18(weights=None)

    wave_model.fc = nn.Sequential(
        nn.Linear(wave_model.fc.in_features, 256),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(256, 2)
    )

    wave_weights = torch.load(wave_path, map_location=DEVICE)
    wave_weights = clean_state_dict(wave_weights)

    wave_model.load_state_dict(wave_weights)

    wave_model.to(DEVICE)
    wave_model.eval()

    MODELS["wave"] = wave_model

    print("✓ Wave model loaded")


    # ====================================
    # Speech Model
    # ====================================

    speech_path = os.path.join(MODEL_DIR, "speech_best_finetuned.pth")

    speech_model = models.resnet18(weights=None)

    speech_model.fc = nn.Sequential(
        nn.Linear(speech_model.fc.in_features, 128),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(128, 2)
    )

    speech_weights = torch.load(speech_path, map_location=DEVICE)
    speech_weights = clean_state_dict(speech_weights)

    speech_model.load_state_dict(speech_weights)

    speech_model.to(DEVICE)
    speech_model.eval()

    MODELS["speech"] = speech_model

    print("✓ Speech model loaded")


    # ====================================
    # Gait Model
    # ====================================

    gait_path = os.path.join(MODEL_DIR, "gait_binary_v1.pth")

    gait_model = GaitBinaryCNN()

    gait_weights = torch.load(gait_path, map_location=DEVICE)

    gait_model.load_state_dict(gait_weights)

    gait_model.to(DEVICE)
    gait_model.eval()

    MODELS["gait"] = gait_model

    print("✓ Gait model loaded")


    print("🚀 All NeuroSeek models loaded successfully")
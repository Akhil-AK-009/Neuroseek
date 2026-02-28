import torch
import numpy as np
from app.core.model_loader import MODELS, DEVICE


# -----------------------------
# 🔹 HANDWRITING INFERENCE
# -----------------------------
def run_handwriting_model(image_tensor, variant="spiral"):
    """
    image_tensor: preprocessed tensor (1,3,224,224)
    variant: 'spiral' or 'wave'
    """

    model = MODELS[variant]

    with torch.no_grad():
        image_tensor = image_tensor.to(DEVICE)
        outputs = model(image_tensor)
        probs = torch.softmax(outputs, dim=1)
        risk_score = probs[0][1].item()  # class 1 = PD

    return risk_score


# -----------------------------
# 🔹 SPEECH INFERENCE
# -----------------------------
def run_speech_model(spectrogram_tensor):
    """
    spectrogram_tensor: (1,3,224,224)
    """

    model = MODELS["speech"]

    with torch.no_grad():
        spectrogram_tensor = spectrogram_tensor.to(DEVICE)
        outputs = model(spectrogram_tensor)
        probs = torch.softmax(outputs, dim=1)
        risk_score = probs[0][1].item()

    return risk_score


# -----------------------------
# 🔹 GAIT INFERENCE
# -----------------------------
def run_gait_model(feature_vector):
    """
    feature_vector: numpy array shape (1, n_features)
    """

    model = MODELS["gait_model"]
    scaler = MODELS["gait_scaler"]
    threshold = MODELS["gait_threshold"]

    scaled_features = scaler.transform(feature_vector)

    prob = model.predict_proba(scaled_features)[0][1]

    return float(prob)


# -----------------------------
# 🔹 WEIGHTED LATE FUSION
# -----------------------------
def compute_final_risk(hw_score, speech_score, gait_score):

    final_score = (
        0.30 * hw_score +
        0.20 * speech_score +
        0.50 * gait_score
    )

    if final_score < 0.35:
        risk_level = "Normal"
    elif final_score < 0.65:
        risk_level = "Moderate"
    else:
        risk_level = "High"

    return final_score, risk_level
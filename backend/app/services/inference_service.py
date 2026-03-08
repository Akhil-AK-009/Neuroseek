import torch
import torchaudio
import numpy as np
from PIL import Image
from torchvision import transforms

from app.core.model_loader import MODELS, DEVICE
from app.services.gait_feature_extractor import extract_gait_features


# -------------------------------------------------
# IMAGE TRANSFORM (Handwriting preprocessing)
# -------------------------------------------------

image_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])


# -------------------------------------------------
# MEL SPECTROGRAM TRANSFORM (Speech)
# -------------------------------------------------

mel_transform = torchaudio.transforms.MelSpectrogram(
    sample_rate=16000,
    n_mels=128
)


# -------------------------------------------------
# HANDWRITING MODEL INFERENCE
# -------------------------------------------------

def run_handwriting_model(image_path, variant="spiral"):

    print(f"[HANDWRITING] Running {variant} model")

    model = MODELS[variant]

    image = Image.open(image_path).convert("RGB")

    tensor = image_transform(image)
    tensor = tensor.unsqueeze(0).to(DEVICE)

    with torch.no_grad():

        outputs = model(tensor)

        probs = torch.softmax(outputs, dim=1)

        risk_score = probs[0][1].item()

    print(f"[HANDWRITING] {variant} score:", risk_score)

    return risk_score


# -------------------------------------------------
# SPEECH MODEL INFERENCE
# -------------------------------------------------

def run_speech_model(audio_path):

    print("[SPEECH] Running speech model")

    model = MODELS["speech"]

    waveform, sr = torchaudio.load(audio_path)

    # convert stereo → mono
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)

    # resample if needed
    if sr != 16000:
        waveform = torchaudio.functional.resample(
            waveform,
            sr,
            16000
        )

    mel = mel_transform(waveform)

    mel = torch.log(mel + 1e-9)

    mel = (mel - mel.mean()) / (mel.std() + 1e-9)

    # fake RGB channels for CNN
    mel = mel.repeat(3, 1, 1)

    mel = mel.unsqueeze(0).to(DEVICE)

    with torch.no_grad():

        outputs = model(mel)

        probs = torch.softmax(outputs, dim=1)

        risk_score = probs[0][1].item()

    print("[SPEECH] score:", risk_score)

    return risk_score


# -------------------------------------------------
# GAIT MODEL INFERENCE
# -------------------------------------------------

def run_gait_model(sequence_tensor):

    print("[GAIT] Running gait CNN")

    model = MODELS["gait"]

    sequence_tensor = sequence_tensor.to(DEVICE)

    with torch.no_grad():

        outputs = model(sequence_tensor)

        probs = torch.softmax(outputs, dim=1)

        risk_score = probs[0][1].item()

    print("[GAIT] score:", risk_score)

    return risk_score


# -------------------------------------------------
# GAIT VIDEO PIPELINE
# -------------------------------------------------

def run_gait_video_inference(video_path):

    print("[GAIT] Extracting pose features")

    sequence_tensor = extract_gait_features(video_path)

    risk_score = run_gait_model(sequence_tensor)

    return risk_score


# -------------------------------------------------
# MULTIMODAL FUSION
# -------------------------------------------------

def compute_final_risk(hw_score, speech_score, gait_score):

    print("[FUSION] Computing final risk")

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

    print("[FUSION] Final score:", final_score)

    return final_score, risk_level


# -------------------------------------------------
# FULL MULTIMODAL INFERENCE
# -------------------------------------------------

def run_full_inference(
    spiral_path=None,
    wave_path=None,
    audio_path=None,
    video_path=None
):

    print("\n========= NEUROSEEK INFERENCE =========")

    handwriting_score = 0
    speech_score = 0
    gait_score = 0

    # ---------------- HANDWRITING ----------------

    if spiral_path is not None and wave_path is not None:

        spiral_score = run_handwriting_model(spiral_path, "spiral")
        wave_score = run_handwriting_model(wave_path, "wave")

        handwriting_score = (spiral_score + wave_score) / 2

        print("[HANDWRITING] combined score:", handwriting_score)

    else:

        print("[HANDWRITING] skipped")


    # ---------------- SPEECH ----------------

    if audio_path is not None:

        speech_score = run_speech_model(audio_path)

    else:

        print("[SPEECH] skipped")


    # ---------------- GAIT ----------------

    if video_path is not None:

        gait_score = run_gait_video_inference(video_path)

    else:

        print("[GAIT] skipped")


    # ---------------- FUSION ----------------

    final_score, risk_level = compute_final_risk(
        handwriting_score,
        speech_score,
        gait_score
    )

    print("========= INFERENCE COMPLETE =========\n")

    return {

        "handwriting_score": handwriting_score,

        "speech_score": speech_score,

        "gait_score": gait_score,

        "final_risk_score": final_score,

        "risk_level": risk_level
    }
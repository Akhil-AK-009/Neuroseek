import torch
import torchaudio
import logging
from PIL import Image
from torchvision import transforms
from pydub import AudioSegment

from app.core.model_loader import MODELS, DEVICE
from app.services.gait_feature_extractor import extract_gait_features

logger = logging.getLogger(__name__)


# -------------------------------------------------
# AUDIO CONVERSION FUNCTION
# -------------------------------------------------

def convert_audio_to_wav(input_path):
    """
    Convert any uploaded audio format to WAV.
    """
    audio = AudioSegment.from_file(input_path)
    wav_path = input_path + ".wav"
    audio.export(wav_path, format="wav")
    return wav_path


# -------------------------------------------------
# IMAGE TRANSFORM (Handwriting)
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
    """
    Runs handwriting model (spiral or wave).
    Returns probability of Parkinson class.
    """
    model = MODELS[variant]

    image = Image.open(image_path).convert("RGB")
    tensor = image_transform(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        outputs = model(tensor)
        probs = torch.softmax(outputs, dim=1)
        risk_score = probs[0][1].item()

    return risk_score


# -------------------------------------------------
# SPEECH MODEL INFERENCE (WITH CALIBRATION)
# -------------------------------------------------

def run_speech_model(audio_path):
    """
    Runs speech model and applies calibration
    to reduce overconfidence.
    """
    model = MODELS["speech"]

    audio_path = convert_audio_to_wav(audio_path)
    waveform, sr = torchaudio.load(audio_path)

    # Convert to mono
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)

    # Resample
    if sr != 16000:
        waveform = torchaudio.functional.resample(waveform, sr, 16000)

    # Ensure fixed length (3 seconds)
    target_length = 16000 * 3
    if waveform.shape[1] > target_length:
        waveform = waveform[:, :target_length]
    else:
        pad = target_length - waveform.shape[1]
        waveform = torch.nn.functional.pad(waveform, (0, pad))

    mel = mel_transform(waveform)
    mel = torch.log(mel + 1e-6)
    mel = (mel - mel.mean()) / (mel.std() + 1e-6)
    mel = mel.repeat(3, 1, 1).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        outputs = model(mel)
        probs = torch.softmax(outputs, dim=1)

        raw_score = probs[0][1].item()

        # Calibration to reduce extreme confidence
        risk_score = 0.6 * raw_score + 0.2

    return risk_score


# -------------------------------------------------
# GAIT MODEL INFERENCE
# -------------------------------------------------

def run_gait_model(sequence_tensor):
    """
    Runs gait CNN model.
    """
    model = MODELS["gait"]
    sequence_tensor = sequence_tensor.to(DEVICE)

    with torch.no_grad():
        outputs = model(sequence_tensor)
        probs = torch.softmax(outputs, dim=1)
        risk_score = probs[0][1].item()

    return risk_score


# -------------------------------------------------
# GAIT VIDEO PIPELINE
# -------------------------------------------------

def run_gait_video_inference(video_path):
    """
    Extracts pose features and runs gait model.
    """
    sequence_tensor = extract_gait_features(video_path)

    if sequence_tensor is None:
        raise ValueError("Gait feature extraction failed")

    return run_gait_model(sequence_tensor)


# -------------------------------------------------
# FULL MULTIMODAL INFERENCE (NO FUSION HERE)
# -------------------------------------------------

def run_full_inference(
    spiral_path=None,
    wave_path=None,
    audio_path=None,
    video_path=None
):
    """
    Runs all modalities and returns raw scores only.
    Fusion is handled in screening_service.
    """

    handwriting_score = 0
    speech_score = 0
    gait_score = 0

    # Handwriting
    if spiral_path and wave_path:
        spiral_score = run_handwriting_model(spiral_path, "spiral")
        wave_score = run_handwriting_model(wave_path, "wave")
        handwriting_score = (spiral_score + wave_score) / 2

    # Speech
    if audio_path:
        speech_score = run_speech_model(audio_path)

    # Gait
    if video_path:
        gait_score = run_gait_video_inference(video_path)

    return {
        "handwriting": handwriting_score,
        "speech": speech_score,
        "gait": gait_score
    }
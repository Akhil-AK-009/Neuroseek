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
    Convert any uploaded audio format to wav.
    Supports: mp3, m4a, ogg, flac, wav, etc.
    """

    audio = AudioSegment.from_file(input_path)

    wav_path = input_path + ".wav"

    audio.export(wav_path, format="wav")

    return wav_path


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

    logger.info(f"[HANDWRITING] Running {variant} model")

    model = MODELS[variant]

    image = Image.open(image_path).convert("RGB")

    tensor = image_transform(image)
    tensor = tensor.unsqueeze(0).to(DEVICE)

    with torch.no_grad():

        outputs = model(tensor)

        probs = torch.softmax(outputs, dim=1)

        risk_score = probs[0][1].item()

    logger.info(f"[HANDWRITING] {variant} score: {risk_score}")

    return risk_score


# -------------------------------------------------
# SPEECH MODEL INFERENCE
# -------------------------------------------------

def run_speech_model(audio_path):

    logger.info("[SPEECH] Running speech model")

    model = MODELS["speech"]

    # Convert uploaded audio to WAV
    audio_path = convert_audio_to_wav(audio_path)

    waveform, sr = torchaudio.load(audio_path)

    # Convert stereo → mono
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)

    # Resample if needed
    if sr != 16000:
        waveform = torchaudio.functional.resample(
            waveform,
            sr,
            16000
        )

    # Ensure fixed 3-second input
    target_length = 16000 * 3

    if waveform.shape[1] > target_length:
        waveform = waveform[:, :target_length]
    else:
        pad = target_length - waveform.shape[1]
        waveform = torch.nn.functional.pad(waveform, (0, pad))

    mel = mel_transform(waveform)

    mel = torch.log(mel + 1e-6)

    mel = (mel - mel.mean()) / (mel.std() + 1e-6)

    # Fake RGB channels for CNN
    mel = mel.repeat(3, 1, 1)

    mel = mel.unsqueeze(0).to(DEVICE)

    with torch.no_grad():

        outputs = model(mel)

        probs = torch.softmax(outputs, dim=1)

        risk_score = probs[0][1].item()

    logger.info(f"[SPEECH] score: {risk_score}")

    return risk_score


# -------------------------------------------------
# GAIT MODEL INFERENCE
# -------------------------------------------------

def run_gait_model(sequence_tensor):

    logger.info("[GAIT] Running gait CNN")

    model = MODELS["gait"]

    sequence_tensor = sequence_tensor.to(DEVICE)

    with torch.no_grad():

        outputs = model(sequence_tensor)

        probs = torch.softmax(outputs, dim=1)

        risk_score = probs[0][1].item()

    logger.info(f"[GAIT] score: {risk_score}")

    return risk_score


# -------------------------------------------------
# GAIT VIDEO PIPELINE
# -------------------------------------------------

def run_gait_video_inference(video_path):

    logger.info("[GAIT] Extracting pose features")

    sequence_tensor = extract_gait_features(video_path)

    if sequence_tensor is None:
        raise ValueError("Gait feature extraction failed")

    risk_score = run_gait_model(sequence_tensor)

    return risk_score


# -------------------------------------------------
# MULTIMODAL FUSION
# -------------------------------------------------

def compute_final_risk(hw_score, speech_score, gait_score):

    logger.info("[FUSION] Computing final risk")

    scores = []
    weights = []

    if hw_score > 0:
        scores.append(hw_score)
        weights.append(0.30)

    if speech_score > 0:
        scores.append(speech_score)
        weights.append(0.20)

    if gait_score > 0:
        scores.append(gait_score)
        weights.append(0.50)

    if len(scores) == 0:
        raise ValueError("No modality provided")

    total_weight = sum(weights)

    normalized_weights = [w / total_weight for w in weights]

    final_score = sum(s * w for s, w in zip(scores, normalized_weights))

    if final_score < 0.35:
        risk_level = "Normal"

    elif final_score < 0.65:
        risk_level = "Moderate"

    else:
        risk_level = "High"

    logger.info(f"[FUSION] Final score: {final_score}")

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

    logger.info("========= NEUROSEEK INFERENCE =========")

    handwriting_score = 0
    speech_score = 0
    gait_score = 0


    # ---------------- HANDWRITING ----------------

    if spiral_path is not None and wave_path is not None:

        spiral_score = run_handwriting_model(spiral_path, "spiral")

        wave_score = run_handwriting_model(wave_path, "wave")

        handwriting_score = (spiral_score + wave_score) / 2

        logger.info(f"[HANDWRITING] combined score: {handwriting_score}")

    else:

        logger.info("[HANDWRITING] skipped")


    # ---------------- SPEECH ----------------

    if audio_path is not None:

        speech_score = run_speech_model(audio_path)

    else:

        logger.info("[SPEECH] skipped")


    # ---------------- GAIT ----------------

    if video_path is not None:

        gait_score = run_gait_video_inference(video_path)

    else:

        logger.info("[GAIT] skipped")


    # ---------------- FUSION ----------------

    final_score, risk_level = compute_final_risk(
        handwriting_score,
        speech_score,
        gait_score
    )

    logger.info("========= INFERENCE COMPLETE =========")

    return {

        "modalities": {

            "handwriting": round(handwriting_score, 3),

            "speech": round(speech_score, 3),

            "gait": round(gait_score, 3)

        },

        "final_result": {

            "risk_score": round(final_score, 3),

            "risk_level": risk_level

        }
    }
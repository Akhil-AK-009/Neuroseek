import torch
import cv2
import numpy as np
import os
import torchaudio
import time

from PIL import Image
from torchvision import transforms

from app.core.model_loader import MODELS, DEVICE


# -------------------------------------------------
# IMAGE TRANSFORM
# -------------------------------------------------

image_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])


# -------------------------------------------------
# CORE GRADCAM FUNCTION
# -------------------------------------------------

def generate_gradcam(model, input_tensor, target_layer):

    gradients = []
    activations = []

    def forward_hook(module, input, output):
        activations.append(output)

    def backward_hook(module, grad_in, grad_out):
        gradients.append(grad_out[0])

    handle_f = target_layer.register_forward_hook(forward_hook)
    handle_b = target_layer.register_full_backward_hook(backward_hook)

    input_tensor = input_tensor.to(DEVICE)

    model.eval()

    output = model(input_tensor)

    class_idx = torch.argmax(output)

    model.zero_grad()

    output[:, class_idx].backward()

    grads = gradients[0]
    acts = activations[0]

    weights = torch.mean(grads, dim=(2, 3), keepdim=True)

    cam = torch.sum(weights * acts, dim=1)

    cam = torch.relu(cam)

    cam = cam.squeeze().cpu().detach().numpy()

    cam = cv2.resize(cam, (224, 224))

    cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)

    handle_f.remove()
    handle_b.remove()

    return cam


# -------------------------------------------------
# HANDWRITING GRADCAM GENERATOR
# -------------------------------------------------

def generate_handwriting_gradcam(model, image_path, target_layer):

    image = Image.open(image_path).convert("RGB")

    tensor = image_transform(image).unsqueeze(0)

    cam = generate_gradcam(model, tensor, target_layer)

    img = cv2.resize(np.array(image), (224, 224))

    heatmap = cv2.applyColorMap(np.uint8(255 * cam), cv2.COLORMAP_JET)

    overlay = heatmap * 0.4 + img

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    output_dir = os.path.join(BASE_DIR, "gradcam_outputs")

    os.makedirs(output_dir, exist_ok=True)

    timestamp = int(time.time())
    base_name = os.path.basename(image_path).split(".")[0]

    filename = f"gradcam_{base_name}_{timestamp}.jpg"
    output_path = os.path.join(output_dir, filename)

    cv2.imwrite(output_path, overlay)

    return filename


# -------------------------------------------------
# SINGLE HANDWRITING EXPLANATION
# -------------------------------------------------

def explain_handwriting(image_path, variant="spiral"):

    model = MODELS[variant]

    target_layer = model.layer4[-1]

    filename = generate_handwriting_gradcam(
        model,
        image_path,
        target_layer
    )

    return filename


# -------------------------------------------------
# SPIRAL + WAVE EXPLANATION
# -------------------------------------------------

def explain_handwriting_pair(spiral_path, wave_path):

    print("[XAI] Generating handwriting Grad-CAM")

    spiral_cam = explain_handwriting(
        spiral_path,
        variant="spiral"
    )

    wave_cam = explain_handwriting(
        wave_path,
        variant="wave"
    )

    return {
        "spiral_gradcam": spiral_cam,
        "wave_gradcam": wave_cam
    }


# -------------------------------------------------
# SPEECH GRADCAM
# -------------------------------------------------

def explain_speech(audio_path):

    model = MODELS["speech"]

    model.eval()

    waveform, sr = torchaudio.load(audio_path)

    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)

    if sr != 16000:
        waveform = torchaudio.functional.resample(
            waveform,
            sr,
            16000
        )

    mel_transform = torchaudio.transforms.MelSpectrogram(
        sample_rate=16000,
        n_mels=128
    )

    mel = mel_transform(waveform)

    mel = torch.log(mel + 1e-9)

    mel = (mel - mel.mean()) / (mel.std() + 1e-9)

    mel = mel.repeat(3, 1, 1)

    tensor = mel.unsqueeze(0).to(DEVICE)

    if hasattr(model, "layer4"):
        target_layer = model.layer4[-1]
    else:
        target_layer = model.backbone.layer4[-1]

    cam = generate_gradcam(
        model,
        tensor,
        target_layer
    )

    spec = mel[0, 0].cpu().numpy()

    spec = (spec - spec.min()) / (spec.max() - spec.min() + 1e-8)

    spec = cv2.resize(spec, (224, 224))

    spec_img = np.uint8(255 * spec)

    spec_img = cv2.cvtColor(spec_img, cv2.COLOR_GRAY2BGR)

    heatmap = cv2.applyColorMap(
        np.uint8(255 * cam),
        cv2.COLORMAP_JET
    )

    overlay = heatmap * 0.4 + spec_img

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    output_dir = os.path.join(BASE_DIR, "gradcam_outputs")

    os.makedirs(output_dir, exist_ok=True)

    timestamp = int(time.time())

    filename = f"speech_gradcam_{timestamp}.png"

    output_path = os.path.join(output_dir, filename)

    cv2.imwrite(output_path, overlay)

    return filename
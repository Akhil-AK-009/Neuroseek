import torch
import cv2
import numpy as np
import os
import torchaudio

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
    handle_b = target_layer.register_backward_hook(backward_hook)

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
# HANDWRITING GRADCAM
# -------------------------------------------------

def generate_handwriting_gradcam(model, image_path, target_layer):

    image = Image.open(image_path).convert("RGB")

    tensor = image_transform(image).unsqueeze(0)

    cam = generate_gradcam(model, tensor, target_layer)

    img = cv2.resize(np.array(image), (224, 224))

    heatmap = cv2.applyColorMap(np.uint8(255 * cam), cv2.COLORMAP_JET)

    overlay = heatmap * 0.4 + img

    os.makedirs("gradcam_outputs", exist_ok=True)

    output_path = f"gradcam_outputs/gradcam_{os.path.basename(image_path)}"

    cv2.imwrite(output_path, overlay)

    return output_path


# -------------------------------------------------
# SINGLE HANDWRITING EXPLANATION
# -------------------------------------------------

def explain_handwriting(image_path, variant="spiral"):

    model = MODELS[variant]

    target_layer = model.layer4[-1]

    output_path = generate_handwriting_gradcam(
        model,
        image_path,
        target_layer
    )

    return output_path


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

    # stereo → mono
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)

    # resample
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

    # Detect correct layer automatically
    if hasattr(model, "layer4"):
        target_layer = model.layer4[-1]
    else:
        target_layer = model.backbone.layer4[-1]

    cam = generate_gradcam(
        model,
        tensor,
        target_layer
    )

    # Convert spectrogram to image
    spec = mel[0,0].cpu().numpy()

    spec = (spec - spec.min()) / (spec.max() - spec.min() + 1e-8)

    spec = cv2.resize(spec, (224,224))

    spec_img = np.uint8(255 * spec)

    spec_img = cv2.cvtColor(spec_img, cv2.COLOR_GRAY2BGR)

    heatmap = cv2.applyColorMap(
        np.uint8(255 * cam),
        cv2.COLORMAP_JET
    )

    overlay = heatmap * 0.4 + spec_img

    os.makedirs("gradcam_outputs", exist_ok=True)

    output_path = "gradcam_outputs/speech_gradcam.png"

    cv2.imwrite(output_path, overlay)

    return output_path
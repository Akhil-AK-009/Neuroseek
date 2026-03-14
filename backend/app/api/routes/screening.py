from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import shutil
import os

from app.api.deps import get_db
from app.models.patient import Patient
from app.models.screening import Screening
from app.schemas.screening import ScreeningCreate
from app.core.security import get_current_user

from app.services.inference_service import (
    run_full_inference,
    run_gait_video_inference
)

from app.services.report_service import generate_screening_report

from app.services.gradcam_service import (
    explain_handwriting_pair,
    explain_speech
)


router = APIRouter(prefix="/screenings", tags=["Screenings"])


# -------------------------------------------------------
# Helper function for saving uploaded files
# -------------------------------------------------------

def save_upload_file(upload_file: UploadFile, folder: str):

    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder, upload_file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return file_path


# -------------------------------------------------------
# HANDWRITING SCREENING
# -------------------------------------------------------

@router.post("/handwriting")
def handwriting_screening(
    patient_id: int,
    spiral: UploadFile = File(...),
    wave: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    spiral_path = save_upload_file(spiral, "temp_handwriting")
    wave_path = save_upload_file(wave, "temp_handwriting")

    try:

        result = run_full_inference(
            spiral_path=spiral_path,
            wave_path=wave_path
        )

        screening = Screening(
            patient_id=patient_id,
            handwriting_score=result["modalities"]["handwriting"],
            speech_score=0.0,
            gait_score=0.0,
            final_risk_score=result["modalities"]["handwriting"],
            risk_level=result["final_result"]["risk_level"],
            is_active=True
        )

        db.add(screening)
        db.commit()
        db.refresh(screening)

        report = generate_screening_report(
            result,
            patient_id,
            screening.id
        )

        return report

    finally:
        if os.path.exists(spiral_path):
            os.remove(spiral_path)
        if os.path.exists(wave_path):
            os.remove(wave_path)


# -------------------------------------------------------
# SPEECH SCREENING
# -------------------------------------------------------

@router.post("/speech")
def speech_screening(
    patient_id: int,
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    audio_path = save_upload_file(audio, "temp_audio")

    try:

        result = run_full_inference(audio_path=audio_path)

        screening = Screening(
            patient_id=patient_id,
            handwriting_score=0.0,
            speech_score=result["modalities"]["speech"],
            gait_score=0.0,
            final_risk_score=result["modalities"]["speech"],
            risk_level=result["final_result"]["risk_level"],
            is_active=True
        )

        db.add(screening)
        db.commit()
        db.refresh(screening)

        report = generate_screening_report(
            result,
            patient_id,
            screening.id
        )

        return report

    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)


# -------------------------------------------------------
# GAIT SCREENING
# -------------------------------------------------------

@router.post("/gait-video")
def gait_video_screening(
    patient_id: int,
    video: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    video_path = save_upload_file(video, "temp_videos")

    try:

        gait_score = run_gait_video_inference(video_path)

        risk_level = "Normal"

        if gait_score >= 0.65:
            risk_level = "High"
        elif gait_score >= 0.35:
            risk_level = "Moderate"

        screening = Screening(
            patient_id=patient_id,
            handwriting_score=0.0,
            speech_score=0.0,
            gait_score=gait_score,
            final_risk_score=gait_score,
            risk_level=risk_level,
            is_active=True
        )

        db.add(screening)
        db.commit()
        db.refresh(screening)

        result = {
            "modalities": {
                "handwriting": 0.0,
                "speech": 0.0,
                "gait": gait_score
            },
            "final_result": {
                "risk_score": gait_score,
                "risk_level": risk_level
            }
        }

        report = generate_screening_report(
            result,
            patient_id,
            screening.id
        )

        return report

    finally:
        if os.path.exists(video_path):
            os.remove(video_path)


# -------------------------------------------------------
# FULL MULTIMODAL SCREENING
# -------------------------------------------------------

@router.post("/full")
def full_multimodal_screening(
    patient_id: int,
    spiral: UploadFile = File(...),
    wave: UploadFile = File(...),
    audio: UploadFile = File(...),
    video: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    spiral_path = save_upload_file(spiral, "temp_uploads")
    wave_path = save_upload_file(wave, "temp_uploads")
    audio_path = save_upload_file(audio, "temp_uploads")
    video_path = save_upload_file(video, "temp_uploads")

    try:

        result = run_full_inference(
            spiral_path=spiral_path,
            wave_path=wave_path,
            audio_path=audio_path,
            video_path=video_path
        )

        screening = Screening(
            patient_id=patient_id,
            handwriting_score=result["modalities"]["handwriting"],
            speech_score=result["modalities"]["speech"],
            gait_score=result["modalities"]["gait"],
            final_risk_score=result["final_result"]["risk_score"],
            risk_level=result["final_result"]["risk_level"],
            is_active=True
        )

        db.add(screening)
        db.commit()
        db.refresh(screening)

        explanations = explain_handwriting_pair(
            spiral_path,
            wave_path
        )

        report = generate_screening_report(
            result,
            patient_id,
            screening.id
        )

        report["explainability"] = explanations

        return report

    finally:

        for path in [spiral_path, wave_path, audio_path, video_path]:
            if os.path.exists(path):
                os.remove(path)


# -------------------------------------------------------
# HANDWRITING GRADCAM API
# -------------------------------------------------------

@router.post("/explain-handwriting")
def explain_handwriting(
    spiral: UploadFile = File(...),
    wave: UploadFile = File(...),
    current_user=Depends(get_current_user)
):

    spiral_path = save_upload_file(spiral, "temp_xai")
    wave_path = save_upload_file(wave, "temp_xai")

    try:

        result = explain_handwriting_pair(
            spiral_path,
            wave_path
        )

        return {
            "message": "Grad-CAM generated successfully",
            "explanations": result
        }

    finally:

        if os.path.exists(spiral_path):
            os.remove(spiral_path)
        if os.path.exists(wave_path):
            os.remove(wave_path)


# -------------------------------------------------------
# SPEECH GRADCAM API
# -------------------------------------------------------

@router.post("/explain-speech")
def explain_speech_api(
    audio: UploadFile = File(...),
    current_user=Depends(get_current_user)
):

    audio_path = save_upload_file(audio, "temp_xai")

    try:

        cam = explain_speech(audio_path)

        return {
            "speech_gradcam": cam
        }

    finally:

        if os.path.exists(audio_path):
            os.remove(audio_path)
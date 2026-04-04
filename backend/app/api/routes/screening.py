from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
import shutil
import os
import time

from app.api.deps import get_db
from app.core.security import get_current_user
from app.models.screening import Screening

from app.services.inference_service import (
    run_handwriting_model,
    run_speech_model,
    run_gait_video_inference
)

from app.services.screening_service import update_screening_session
from app.services.gradcam_service import (
    explain_handwriting_pair,
    explain_speech
)

router = APIRouter(prefix="/screenings", tags=["Screenings"])


# ---------------- FILE SAVE ----------------
def save_upload_file(upload_file: UploadFile, folder: str):
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, upload_file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return file_path


# ---------------- SAFE DELETE ----------------
def safe_delete(path: str):
    try:
        time.sleep(1)
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        print(f"[WARNING] Could not delete file {path}: {e}")


# ---------------- HANDWRITING ----------------
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
        spiral_score = run_handwriting_model(spiral_path, "spiral")
        wave_score = run_handwriting_model(wave_path, "wave")

        handwriting_score = (spiral_score + wave_score) / 2

        screening = update_screening_session(
            db=db,
            patient_id=patient_id,
            modality="handwriting",
            score=handwriting_score,
            user_id=current_user.id
        )

        return {
            "message": "Handwriting screening completed",
            "handwriting_score": round(handwriting_score, 3),
            "final_risk_score": screening.final_risk_score,
            "risk_level": screening.risk_level,
            "modalities_present": screening.modalities_present,
            "is_complete": screening.is_complete
        }

    finally:
        safe_delete(spiral_path)
        safe_delete(wave_path)


# ---------------- SPEECH ----------------
@router.post("/speech")
def speech_screening(
    patient_id: int,
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    audio_path = save_upload_file(audio, "temp_audio")

    try:
        speech_score = run_speech_model(audio_path)

        screening = update_screening_session(
            db=db,
            patient_id=patient_id,
            modality="speech",
            score=speech_score,
            user_id=current_user.id
        )

        return {
            "message": "Speech screening completed",
            "speech_score": round(speech_score, 3),
            "final_risk_score": screening.final_risk_score,
            "risk_level": screening.risk_level,
            "modalities_present": screening.modalities_present,
            "is_complete": screening.is_complete
        }

    finally:
        safe_delete(audio_path)


# ---------------- GAIT ----------------
@router.post("/gait")
def gait_screening(
    patient_id: int,
    video: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    video_path = save_upload_file(video, "temp_videos")

    try:
        try:
            gait_score = run_gait_video_inference(video_path)
        except Exception as e:
            print(f"[GAIT ERROR] {e}")
            gait_score = 0.5

        screening = update_screening_session(
            db=db,
            patient_id=patient_id,
            modality="gait",
            score=gait_score,
            user_id=current_user.id
        )

        return {
            "message": "Gait screening completed",
            "gait_score": round(gait_score, 3),
            "final_risk_score": screening.final_risk_score,
            "risk_level": screening.risk_level,
            "modalities_present": screening.modalities_present,
            "is_complete": screening.is_complete
        }

    finally:
        safe_delete(video_path)


# ---------------- FULL MULTIMODAL ----------------
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
        spiral_score = run_handwriting_model(spiral_path, "spiral")
        wave_score = run_handwriting_model(wave_path, "wave")
        handwriting_score = (spiral_score + wave_score) / 2

        speech_score = run_speech_model(audio_path)

        try:
            gait_score = run_gait_video_inference(video_path)
        except Exception as e:
            print(f"[GAIT ERROR] {e}")
            gait_score = 0.5

        screening = update_screening_session(db, patient_id, "handwriting", handwriting_score, current_user.id)
        screening = update_screening_session(db, patient_id, "speech", speech_score, current_user.id)
        screening = update_screening_session(db, patient_id, "gait", gait_score, current_user.id)

        explanations = explain_handwriting_pair(spiral_path, wave_path)

        return {
            "message": "Full screening completed",

            "modalities": {
                "handwriting": round(handwriting_score, 3),
                "speech": round(speech_score, 3),
                "gait": round(gait_score, 3)
            },

            "final_result": {
                "risk_score": screening.final_risk_score,
                "risk_level": screening.risk_level
            },

            "explainability": {
                "spiral_gradcam": f"/gradcam_outputs/{explanations['spiral_gradcam']}",
                "wave_gradcam": f"/gradcam_outputs/{explanations['wave_gradcam']}"
            },

            "modalities_present": screening.modalities_present,
            "is_complete": screening.is_complete,

            "report": {
                "id": screening.id,
                "patient_name": screening.patient.full_name,
                "patient_age": screening.patient.age,
                "patient_gender": screening.patient.gender,
                "handwriting_score": screening.handwriting_score,
                "speech_score": screening.speech_score,
                "gait_score": screening.gait_score,
                "final_score": screening.final_risk_score,
                "risk_level": screening.risk_level,
                "date": screening.created_at.strftime("%Y-%m-%d")
            }
        }

    finally:
        safe_delete(spiral_path)
        safe_delete(wave_path)
        safe_delete(audio_path)
        safe_delete(video_path)


# ---------------- HISTORY (FIXED) ----------------
@router.get("/history")
def get_screening_history(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    screenings = (
        db.query(Screening)
        .join(Screening.patient)
        .filter(
            Screening.is_active == True,
            Screening.patient.has(created_by=current_user.id)
        )
        .order_by(Screening.created_at.desc())
        .all()
    )

    result = []

    for s in screenings:
        result.append({
            "id": s.id,
            "patient_name": s.patient.full_name,
            "patient_age": s.patient.age,
            "patient_gender": s.patient.gender,
            "handwriting_score": s.handwriting_score,
            "speech_score": s.speech_score,
            "gait_score": s.gait_score,
            "final_score": s.final_risk_score,
            "risk_level": s.risk_level,
            "date": s.created_at.strftime("%Y-%m-%d")
        })

    return result
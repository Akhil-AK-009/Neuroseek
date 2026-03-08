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

router = APIRouter(prefix="/screenings", tags=["Screenings"])


# ------------------ CREATE SCREENING (EMPTY) ------------------

@router.post("")
def create_screening(
    data: ScreeningCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    patient = db.query(Patient).filter(
        Patient.id == data.patient_id,
        Patient.created_by == current_user.id,
        Patient.is_active == True
    ).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    inference_result = run_full_inference()

    screening = Screening(
        patient_id=data.patient_id,
        handwriting_score=inference_result["handwriting_score"],
        speech_score=inference_result["speech_score"],
        gait_score=inference_result["gait_score"],
        final_risk_score=inference_result["final_risk_score"],
        risk_level=inference_result["risk_level"],
        is_active=True
    )

    db.add(screening)
    db.commit()
    db.refresh(screening)

    return screening


# ------------------ HANDWRITING SCREENING ------------------

@router.post("/handwriting")
def handwriting_screening(
    patient_id: int,
    spiral: UploadFile = File(...),
    wave: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.created_by == current_user.id,
        Patient.is_active == True
    ).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    os.makedirs("temp_handwriting", exist_ok=True)

    spiral_path = f"temp_handwriting/{spiral.filename}"
    wave_path = f"temp_handwriting/{wave.filename}"

    with open(spiral_path, "wb") as buffer:
        shutil.copyfileobj(spiral.file, buffer)

    with open(wave_path, "wb") as buffer:
        shutil.copyfileobj(wave.file, buffer)

    result = run_full_inference(
        spiral_path=spiral_path,
        wave_path=wave_path
    )

    screening = Screening(
        patient_id=patient_id,
        handwriting_score=result["handwriting_score"],
        speech_score=0.0,
        gait_score=0.0,
        final_risk_score=result["handwriting_score"],
        risk_level=result["risk_level"],
        is_active=True
    )

    db.add(screening)
    db.commit()
    db.refresh(screening)

    return screening


# ------------------ SPEECH SCREENING ------------------

@router.post("/speech")
def speech_screening(
    patient_id: int,
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.created_by == current_user.id,
        Patient.is_active == True
    ).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    os.makedirs("temp_audio", exist_ok=True)

    audio_path = f"temp_audio/{audio.filename}"

    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    result = run_full_inference(
        audio_path=audio_path
    )

    screening = Screening(
        patient_id=patient_id,
        handwriting_score=0.0,
        speech_score=result["speech_score"],
        gait_score=0.0,
        final_risk_score=result["speech_score"],
        risk_level=result["risk_level"],
        is_active=True
    )

    db.add(screening)
    db.commit()
    db.refresh(screening)

    return screening


# ------------------ GAIT SCREENING ------------------

@router.post("/gait-video")
def gait_video_screening(
    patient_id: int,
    video: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.created_by == current_user.id,
        Patient.is_active == True
    ).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    os.makedirs("temp_videos", exist_ok=True)

    video_path = f"temp_videos/{video.filename}"

    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)

    gait_score = run_gait_video_inference(video_path)

    screening = Screening(
        patient_id=patient_id,
        handwriting_score=0.0,
        speech_score=0.0,
        gait_score=gait_score,
        final_risk_score=gait_score,
        risk_level="Moderate" if gait_score < 0.65 else "High",
        is_active=True
    )

    db.add(screening)
    db.commit()
    db.refresh(screening)

    return screening


# ------------------ FULL MULTIMODAL SCREENING ------------------

@router.post("/full")
def full_multimodal_screening(
    patient_id: int,
    spiral: UploadFile = File(...),
    wave: UploadFile = File(...),
    audio: UploadFile = File(...),
    video: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.created_by == current_user.id,
        Patient.is_active == True
    ).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    os.makedirs("temp_uploads", exist_ok=True)

    spiral_path = f"temp_uploads/{spiral.filename}"
    wave_path = f"temp_uploads/{wave.filename}"
    audio_path = f"temp_uploads/{audio.filename}"
    video_path = f"temp_uploads/{video.filename}"

    with open(spiral_path, "wb") as buffer:
        shutil.copyfileobj(spiral.file, buffer)

    with open(wave_path, "wb") as buffer:
        shutil.copyfileobj(wave.file, buffer)

    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)

    result = run_full_inference(
        spiral_path=spiral_path,
        wave_path=wave_path,
        audio_path=audio_path,
        video_path=video_path
    )

    screening = Screening(
        patient_id=patient_id,
        handwriting_score=result["handwriting_score"],
        speech_score=result["speech_score"],
        gait_score=result["gait_score"],
        final_risk_score=result["final_risk_score"],
        risk_level=result["risk_level"],
        is_active=True
    )

    db.add(screening)
    db.commit()
    db.refresh(screening)

    return screening


# ------------------ GET PATIENT SCREENINGS ------------------

@router.get("/patient/{patient_id}")
def get_patient_screenings(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    screenings = db.query(Screening).join(Patient).filter(
        Screening.patient_id == patient_id,
        Patient.created_by == current_user.id,
        Screening.is_active == True
    ).all()

    return screenings


# ------------------ GET SCREENING DETAIL ------------------

@router.get("/{screening_id}")
def get_screening_detail(
    screening_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    screening = db.query(Screening).join(Patient).filter(
        Screening.id == screening_id,
        Patient.created_by == current_user.id
    ).first()

    if not screening:
        raise HTTPException(status_code=404, detail="Screening not found")

    return screening


# ------------------ DELETE SCREENING ------------------

@router.delete("/{screening_id}")
def delete_screening(
    screening_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    screening = db.query(Screening).join(Patient).filter(
        Screening.id == screening_id,
        Patient.created_by == current_user.id
    ).first()

    if not screening:
        raise HTTPException(status_code=404, detail="Screening not found")

    screening.is_active = False
    db.commit()

    return {"message": "Screening deleted successfully"}


# ------------------ RESTORE SCREENING ------------------

@router.put("/{screening_id}/restore")
def restore_screening(
    screening_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    screening = db.query(Screening).join(Patient).filter(
        Screening.id == screening_id,
        Patient.created_by == current_user.id
    ).first()

    if not screening:
        raise HTTPException(status_code=404, detail="Screening not found")

    screening.is_active = True
    db.commit()

    return {"message": "Screening restored"}
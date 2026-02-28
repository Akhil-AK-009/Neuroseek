# app/api/routes/screening.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.patient import Patient
from app.models.screening import Screening
from app.schemas.screening import ScreeningCreate
from app.core.security import get_current_user
from app.services.inference_service import run_full_inference


router = APIRouter(prefix="/screenings", tags=["Screenings"])





# ------------------ CREATE SCREENING ------------------

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
        raise HTTPException(status_code=404, detail="Patient not found or unauthorized")

    inference_result = run_full_inference()

    new_screening = Screening(
        patient_id=data.patient_id,
        handwriting_score=inference_result["handwriting_score"],
        speech_score=inference_result["speech_score"],
        gait_score=inference_result["gait_score"],
        final_risk_score=inference_result["final_risk_score"],
        risk_level=inference_result["risk_level"],
        is_active=True
    )

    db.add(new_screening)
    db.commit()
    db.refresh(new_screening)

    return {
        "screening_id": new_screening.id,
        "final_risk_score": new_screening.final_risk_score,
        "risk_level": new_screening.risk_level
    }


# ------------------ GET SCREENINGS FOR PATIENT ------------------

@router.get("/patient/{patient_id}")
def get_patient_screenings(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.created_by == current_user.id,
        Patient.is_active == True
    ).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found or unauthorized")

    screenings = db.query(Screening).filter(
        Screening.patient_id == patient_id,
        Screening.is_active == True
    ).all()

    return [
        {
            "screening_id": screening.id,
            "final_risk_score": screening.final_risk_score,
            "risk_level": screening.risk_level,
            "created_at": screening.created_at
        }
        for screening in screenings
    ]


# ------------------ SOFT DELETE SCREENING ------------------

@router.delete("/{screening_id}")
def soft_delete_screening(
    screening_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    screening = db.query(Screening).join(Patient).filter(
        Screening.id == screening_id,
        Patient.created_by == current_user.id,
        Screening.is_active == True
    ).first()

    if not screening:
        raise HTTPException(status_code=404, detail="Screening not found or unauthorized")

    screening.is_active = False
    db.commit()

    return {"message": "Screening deleted successfully (soft delete) 🗑️"}


# ------------------ RESTORE SCREENING ------------------

@router.put("/{screening_id}/restore")
def restore_screening(
    screening_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    screening = db.query(Screening).join(Patient).filter(
        Screening.id == screening_id,
        Patient.created_by == current_user.id,
        Screening.is_active == False
    ).first()

    if not screening:
        raise HTTPException(
            status_code=404,
            detail="Screening not found, already active, or unauthorized"
        )

    screening.is_active = True
    db.commit()

    return {"message": "Screening restored successfully ♻️"}
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
        raise HTTPException(status_code=404, detail="Screening not found or unauthorized")

    return {
        "screening_id": screening.id,
        "handwriting_score": screening.handwriting_score,
        "speech_score": screening.speech_score,
        "gait_score": screening.gait_score,
        "final_risk_score": screening.final_risk_score,
        "risk_level": screening.risk_level,
        "created_at": screening.created_at
    }
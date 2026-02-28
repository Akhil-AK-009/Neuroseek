# app/api/routes/patient.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate
from app.core.security import get_current_user


router = APIRouter(prefix="/patients", tags=["Patients"])


# ------------------ CREATE PATIENT ------------------

@router.post("")
def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    new_patient = Patient(
        full_name=patient.full_name,
        age=patient.age,
        gender=patient.gender,
        phone=patient.phone,
        created_by=current_user.id,
        is_active=True
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return {
        "id": new_patient.id,
        "message": "Patient created successfully ✅"
    }


# ------------------ GET ALL PATIENTS ------------------

@router.get("")
def get_all_patients(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    patients = db.query(Patient).filter(
        Patient.created_by == current_user.id,
        Patient.is_active == True
    ).all()

    return [
        {
            "id": patient.id,
            "full_name": patient.full_name,
            "age": patient.age,
            "gender": patient.gender,
            "phone": patient.phone,
            "created_at": patient.created_at
        }
        for patient in patients
    ]


# ------------------ UPDATE PATIENT ------------------

@router.put("/{patient_id}")
def update_patient(
    patient_id: int,
    updated_data: PatientUpdate,
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

    if updated_data.full_name is not None:
        patient.full_name = updated_data.full_name
    if updated_data.age is not None:
        patient.age = updated_data.age
    if updated_data.gender is not None:
        patient.gender = updated_data.gender
    if updated_data.phone is not None:
        patient.phone = updated_data.phone

    db.commit()

    return {"message": "Patient updated successfully ✅"}


# ------------------ SOFT DELETE PATIENT ------------------

@router.delete("/{patient_id}")
def soft_delete_patient(
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

    patient.is_active = False
    db.commit()

    return {"message": "Patient deleted successfully (soft delete) 🗑️"}
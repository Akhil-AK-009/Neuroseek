from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import engine, SessionLocal
from app.db.base import Base

# Models
from app.models.user import User
from app.models.patient import Patient
from app.models.screening import Screening

# Schemas
from app.schemas.user import UserCreate
from app.schemas.patient import PatientCreate, PatientUpdate
from app.schemas.screening import ScreeningCreate

# Security
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

# ML Service
from app.services.inference_service import run_full_inference


app = FastAPI(title="NeuroSeek API")

Base.metadata.create_all(bind=engine)


# ------------------ DATABASE DEPENDENCY ------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------ ROOT ------------------

@app.get("/")
def root():
    return {"message": "NeuroSeek Backend Running 🚀"}


@app.get("/test-db")
def test_db():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"database_status": "Connected ✅"}


# ------------------ REGISTER ------------------

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = hash_password(user.password)

    new_user = User(
        email=user.email,
        hashed_password=hashed_pwd
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully ✅"}


# ------------------ LOGIN ------------------

@app.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if not existing_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not verify_password(user.password, existing_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": existing_user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ------------------ CREATE PATIENT ------------------

@app.post("/patients")
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

@app.get("/patients")
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

@app.put("/patients/{patient_id}")
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

@app.delete("/patients/{patient_id}")
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


# ------------------ CREATE SCREENING ------------------

@app.post("/screenings")
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

@app.get("/patients/{patient_id}/screenings")
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

@app.delete("/screenings/{screening_id}")
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

@app.put("/screenings/{screening_id}/restore")
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


# ------------------ PROFILE ------------------

@app.get("/profile")
def get_profile(current_user = Depends(get_current_user)):
    return {
        "email": current_user.email,
        "message": "Protected profile access successful 🔐"
    }

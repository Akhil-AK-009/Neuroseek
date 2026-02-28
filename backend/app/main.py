from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import engine
from app.db.base import Base

# Models
from app.models.user import User

# Schemas
from app.schemas.user import UserCreate

# Security
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

# 🔹 Routers
from app.api.routes.patient import router as patient_router
from app.api.routes.screening import router as screening_router

# 🔹 DB Dependency
from app.api.deps import get_db

# 🔥 NEW: Model Loader
from app.core.model_loader import load_models


app = FastAPI(title="NeuroSeek API")

# 🔹 Create DB Tables
Base.metadata.create_all(bind=engine)

# 🔹 Register Routers
app.include_router(patient_router)
app.include_router(screening_router)


# --------------------------------------------------
#  STARTUP EVENT — LOAD ML MODELS ONCE
# --------------------------------------------------
@app.on_event("startup")
def startup_event():
    load_models()


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


# ------------------ PROFILE ------------------

@app.get("/profile")
def get_profile(current_user=Depends(get_current_user)):
    return {
        "email": current_user.email,
        "message": "Protected profile access successful 🔐"
    }
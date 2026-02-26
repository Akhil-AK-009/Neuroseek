from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Screening(Base):
    __tablename__ = "screenings"

    id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)

    # Individual modality scores (can be null initially)
    handwriting_score = Column(Float, nullable=True)
    speech_score = Column(Float, nullable=True)
    gait_score = Column(Float, nullable=True)

    # Fusion output
    final_risk_score = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)

    # 🔥 NEW: Track which modalities are present
    modalities_present = Column(String, nullable=True)

    # 🔥 NEW: Track whether session is complete (all 3 provided)
    is_complete = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Soft delete
    is_active = Column(Boolean, default=True)

    # Relationship
    patient = relationship("Patient", back_populates="screenings")
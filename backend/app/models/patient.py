from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    phone = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    #  Ownership
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    #  Soft delete column
    is_active = Column(Boolean, default=True)

    # Relationships
    screenings = relationship("Screening", back_populates="patient",cascade="all, delete-orphan")
    owner = relationship("User")

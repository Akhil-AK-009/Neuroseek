from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    action = Column(String, nullable=False)  # CREATE, UPDATE, DELETE, VIEW, INFERENCE
    entity = Column(String, nullable=False)  # Patient, Screening, User
    entity_id = Column(Integer, nullable=True)

    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")

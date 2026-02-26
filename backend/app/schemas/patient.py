from pydantic import BaseModel
from typing import Optional


class PatientCreate(BaseModel):
    full_name: str
    age: int
    gender: str
    phone: Optional[str] = None


class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    phone: Optional[str] = None

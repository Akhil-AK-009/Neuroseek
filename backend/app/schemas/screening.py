from pydantic import BaseModel

class ScreeningCreate(BaseModel):
    patient_id: int

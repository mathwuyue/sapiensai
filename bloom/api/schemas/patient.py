from typing import Optional
from datetime import date
from pydantic import BaseModel

class PatientBase(BaseModel):
    name: str
    date_of_birth: date
    blood_type: Optional[str] = None
    rh_factor: Optional[str] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None

class PatientCreate(PatientBase):
    user_id: int

class PatientUpdate(PatientBase):
    pass

class PatientInDBBase(PatientBase):
    user_id: int

    class Config:
        from_attributes = True

class Patient(PatientInDBBase):
    pass 
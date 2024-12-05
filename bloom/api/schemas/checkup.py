from typing import Optional
from datetime import date
from pydantic import BaseModel

class CheckupBase(BaseModel):
    user_id: int
    pregnancy_week: Optional[int] = None
    checkup_date: date
    doctor_id: Optional[int] = None
    next_appointment: Optional[date] = None
    notes: Optional[str] = None

class CheckupCreate(CheckupBase):
    pass

class CheckupUpdate(CheckupBase):
    user_id: Optional[int] = None
    checkup_date: Optional[date] = None

class CheckupInDBBase(CheckupBase):
    id: int

    class Config:
        from_attributes = True

class Checkup(CheckupInDBBase):
    pass 
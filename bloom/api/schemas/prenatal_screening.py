from typing import Optional
from datetime import date
from pydantic import BaseModel

class PrenatalScreeningBase(BaseModel):
    checkup_id: int
    screening_type: str
    screening_date: date
    result: Optional[str] = None
    risk_assessment: Optional[str] = None
    notes: Optional[str] = None

class PrenatalScreeningCreate(PrenatalScreeningBase):
    pass

class PrenatalScreeningUpdate(PrenatalScreeningBase):
    checkup_id: Optional[int] = None
    screening_type: Optional[str] = None
    screening_date: Optional[date] = None

class PrenatalScreeningInDBBase(PrenatalScreeningBase):
    id: int

    class Config:
        from_attributes = True

class PrenatalScreening(PrenatalScreeningInDBBase):
    pass 
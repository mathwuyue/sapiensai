from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, condecimal

class LabResultsBase(BaseModel):
    checkup_id: int
    hemoglobin: Optional[condecimal(max_digits=4, decimal_places=1)] = None
    blood_glucose: Optional[condecimal(max_digits=4, decimal_places=1)] = None
    hbsag: Optional[str] = None
    hiv: Optional[str] = None
    syphilis: Optional[str] = None
    tsh: Optional[condecimal(max_digits=5, decimal_places=2)] = None
    urine_protein: Optional[str] = None
    urine_glucose: Optional[str] = None
    notes: Optional[str] = None

class LabResultsCreate(LabResultsBase):
    pass

class LabResultsUpdate(LabResultsBase):
    checkup_id: Optional[int] = None

class LabResultsInDBBase(LabResultsBase):
    id: int

    class Config:
        from_attributes = True

class LabResults(LabResultsInDBBase):
    pass 
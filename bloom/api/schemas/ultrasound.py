from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, condecimal

class UltrasoundBase(BaseModel):
    checkup_id: int
    head_circumference: Optional[condecimal(max_digits=4, decimal_places=1)] = None
    abdominal_circumference: Optional[condecimal(max_digits=4, decimal_places=1)] = None
    femur_length: Optional[condecimal(max_digits=4, decimal_places=1)] = None
    estimated_weight: Optional[condecimal(max_digits=6, decimal_places=2)] = None
    fetal_position: Optional[str] = None
    amniotic_fluid_index: Optional[condecimal(max_digits=4, decimal_places=1)] = None
    placenta_position: Optional[str] = None
    placenta_grade: Optional[int] = None

class UltrasoundCreate(UltrasoundBase):
    pass

class UltrasoundUpdate(UltrasoundBase):
    checkup_id: Optional[int] = None

class UltrasoundInDBBase(UltrasoundBase):
    id: int

    class Config:
        from_attributes = True

class Ultrasound(UltrasoundInDBBase):
    pass 
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, condecimal

class VitalSignsBase(BaseModel):
    checkup_id: int
    weight: Optional[condecimal(max_digits=5, decimal_places=2)] = None
    weight_gain: Optional[condecimal(max_digits=4, decimal_places=2)] = None
    blood_pressure_sys: Optional[int] = None
    blood_pressure_dia: Optional[int] = None
    temperature: Optional[condecimal(max_digits=3, decimal_places=1)] = None
    fundal_height: Optional[condecimal(max_digits=4, decimal_places=1)] = None
    fetal_heart_rate: Optional[int] = None

class VitalSignsCreate(VitalSignsBase):
    pass

class VitalSignsUpdate(VitalSignsBase):
    checkup_id: Optional[int] = None

class VitalSignsInDBBase(VitalSignsBase):
    id: int

    class Config:
        from_attributes = True

class VitalSigns(VitalSignsInDBBase):
    pass 
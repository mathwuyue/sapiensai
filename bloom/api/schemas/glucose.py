from pydantic import BaseModel
from datetime import date
from typing import Optional, List

# shared properties
class GlucoseBase(BaseModel):
    glucose_value: float
    glucose_date: date
    measurement_type: int

# create schema
class GlucoseCreate(GlucoseBase):
    pass

# update schema
class GlucoseUpdate(BaseModel):
    glucose_value: Optional[float] = None
    glucose_date: Optional[date] = None
    measurement_type: Optional[int] = None

# return schema
class Glucose(GlucoseBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class GlucoseReadingResponse(BaseModel):
    datetime: date
    glu: float
    type: int

class GlucoseListResponse(BaseModel):
    total: int
    data: List[GlucoseReadingResponse]
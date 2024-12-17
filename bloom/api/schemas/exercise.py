from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ExerciseCreate(BaseModel):
    exercise: str
    duration: int
    calories: int
    intensity: str
    bpm: Optional[int] = None
    start_time: datetime
    remark: Optional[str] = None
    summary: Optional[str] = None
    advice: Optional[str] = None


class ExerciseResponse(BaseModel):
    id: int
    exercise: str
    duration: int
    calories: float
    intensity: str
    bpm: Optional[int]
    remark: Optional[str]
    #summary: Optional[str] = None
    #advice: Optional[str] = None
    start_time: datetime
    created_at: datetime
    updated_at: datetime
    emma: Optional[str] = None

    class Config:
        from_attributes = True
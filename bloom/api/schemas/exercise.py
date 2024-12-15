from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ExerciseResponse(BaseModel):
    id: int
    exercise: str
    duration: int
    calories: float
    intensity: str
    bpm: Optional[int]
    remark: Optional[str]
    start_time: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
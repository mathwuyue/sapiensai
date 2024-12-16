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
    emma: Optional[str] = None     # 实际存储 JSON 的字段


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

    class Config:
        from_attributes = True
from typing import Optional
from datetime import date
from pydantic import BaseModel

class RecommendationBase(BaseModel):
    checkup_id: int
    category: str
    content: str
    priority: Optional[str] = None
    valid_until: Optional[date] = None
    notes: Optional[str] = None

class RecommendationCreate(RecommendationBase):
    pass

class RecommendationUpdate(RecommendationBase):
    checkup_id: Optional[int] = None
    category: Optional[str] = None
    content: Optional[str] = None

class RecommendationInDBBase(RecommendationBase):
    id: int

    class Config:
        from_attributes = True

class Recommendation(RecommendationInDBBase):
    pass 
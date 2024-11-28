from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class FoodItem(BaseModel):
    name: str
    calories: float
    portion: Optional[str] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None

class FoodAnalysis(BaseModel):
    items: List[FoodItem]
    total_calories: float
    image_description: str
    analysis_date: datetime = datetime.now()

    class Config:
        from_attributes = True 
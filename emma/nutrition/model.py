from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid


class NutritionMacro(BaseModel):
    calories: float
    protein: float
    fat: float
    carb: float


class NutritionMicro(BaseModel):
    fa: float
    vc: float
    vd: float


class NutritionMineral(BaseModel):
    calcium: float
    iron: float
    zinc: float
    iodine: float
    
    
class DietarySummary(BaseModel):
    comment: Optional[str] = Field(default='', description="Comment for dietary")
    advice: Optional[str] = Field(default='', description="Advice for dietary")
    tables: Optional[List[Dict[str, Any]]] = Field(default=[], description="Tables for dietary")
    charts: Optional[List[Dict[str, Any]]] = Field(default=[], description="Charts for dietary")


class DietaryData(BaseModel):
    day: int
    meals: List[str]
    
    
class EmmaComment(BaseModel):
    comment: str
    advice: str = ''
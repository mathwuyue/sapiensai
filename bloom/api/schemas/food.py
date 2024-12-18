from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# 基础模型
class FoodItem(BaseModel):
    """Food item with quantity"""
    food: str
    count: float

class MacroNutrients(BaseModel):
    """Macronutrients information"""
    calories: float
    protein: float
    fat: float
    carb: float

class MicroNutrients(BaseModel):
    """Micronutrients information"""
    fa: float  # 膳食纤维(g)
    vc: float  # 维生素C(mg)
    vd: float  # 维生素D(mcg)

class Minerals(BaseModel):
    """Minerals information"""
    calcium: float  # 钙(mg)
    iron: float    # 铁(mg)
    zinc: float    # 锌(mg)
    iodine: float  # 碘(mcg)

class Nutrients(BaseModel):
    """Combined nutrients information"""
    macro: MacroNutrients
    micro: MicroNutrients
    mineral: Minerals

# 创建和更新模型
class FoodAnalyzeBase(BaseModel):
    """Base schema for food analysis"""
    foods: List[FoodItem]
    nutrients: Nutrients
    summary: str
    advice: str

class FoodAnalyzeCreate(FoodAnalyzeBase):
    """Schema for creating food analysis"""
    file_path: str
    original_filename: str
    content_type: str

class FoodAnalyzeUpdate(FoodAnalyzeBase):
    """Schema for updating food analysis"""
    pass

# 响应模型
class FoodAnalyze(FoodAnalyzeBase):
    """Schema for food analysis response"""
    user_id: int
    file_path: str
    original_filename: str
    created_at: datetime
    class Config:
        from_attributes = True
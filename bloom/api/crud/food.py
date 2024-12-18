from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from fastapi import HTTPException

from api.crud.base import CRUDBase
from api.models.food import FoodAnalyze
from api.schemas.food import FoodAnalyzeCreate, FoodAnalyzeUpdate, FoodAnalyze as FoodAnalyzeSchema

class CRUDFoodAnalyze(CRUDBase[FoodAnalyze, FoodAnalyzeCreate, FoodAnalyzeUpdate]):
    """CRUD operations for food analysis"""
    
    async def create_with_user(
        self, db: AsyncSession, *, obj_in: FoodAnalyzeCreate, user_id: int
    ) -> FoodAnalyze:
        """Create new food analysis for user"""
        nutrients = obj_in.nutrients
        foods_json = [food.model_dump() for food in obj_in.foods]
        
        db_obj = FoodAnalyze(
            user_id=user_id,
            file_path=obj_in.file_path,
            original_filename=obj_in.original_filename,
            content_type=obj_in.content_type,
            foods=foods_json,
            calories=nutrients.macro.calories,
            protein=nutrients.macro.protein,
            fat=nutrients.macro.fat,
            carb=nutrients.macro.carb,
            dietary_fiber=nutrients.micro.fa,
            vitamin_c=nutrients.micro.vc,
            vitamin_d=nutrients.micro.vd,
            calcium=nutrients.mineral.calcium,
            iron=nutrients.mineral.iron,
            zinc=nutrients.mineral.zinc,
            iodine=nutrients.mineral.iodine,
            summary=obj_in.summary,
            advice=obj_in.advice
        )
        
        db.add(db_obj)
        return db_obj

    async def get_multi_by_user(
        self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[FoodAnalyze]:
        """Get multiple food analyses for user"""
        query = (
            select(FoodAnalyze)
            .where(FoodAnalyze.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(FoodAnalyze.created_at.desc())
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_id_and_user(
        self, db: AsyncSession, *, id: int, user_id: int
    ) -> Optional[FoodAnalyze]:
        """Get food analysis by ID and user ID"""
        query = select(FoodAnalyze).where(
            FoodAnalyze.id == id,
            FoodAnalyze.user_id == user_id
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

food = CRUDFoodAnalyze(FoodAnalyze) 
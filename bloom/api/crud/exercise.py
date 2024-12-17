from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, desc, cast, String
from datetime import datetime
from api.schemas.exercise import ExerciseCreate
import json

from api.models.exercise import Exercise

class CRUDExercise:
    async def update_exercise_feedback(
    db: AsyncSession,
    id: int,
    summary: str,
    advice: str
    ) -> Exercise:
        """更新运动记录的 AI 反馈到 emma 列"""
    
    # 构建 emma JSON
        emma_data = {
            "summary": summary,
            "advice": advice
        }

    # 使用 SQLAlchemy update
        stmt = (
            update(Exercise)
            .where(Exercise.id == id)
            .values(emma=json.dumps(emma_data))
            .returning(Exercise)
        )
    
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    
    

class CRUDExercise:
    async def get_multi_by_user(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        summary: Optional[str] = None,
        advice: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Exercise]:
        user_id_str = str(user_id)

        query = select(Exercise)\
            .filter(Exercise.user_id == user_id_str)\
            .order_by(desc(Exercise.start_time))\
            .offset(skip)\
            .limit(limit)
        
        if start_date:
            query = query.filter(Exercise.start_time >= start_date)
        if end_date:
            query = query.filter(Exercise.start_time <= end_date)
            
        result = await db.execute(query)
        return result.scalars().all()
    
    async def remove(
    self,
    db: AsyncSession,
        id: int
    ) -> bool:
        """删除运动记录"""
        stmt = delete(Exercise).where(Exercise.id == id)
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0

exercise = CRUDExercise()
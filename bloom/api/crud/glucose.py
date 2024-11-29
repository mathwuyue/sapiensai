from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.models.glucose import Glucose
from api.schemas.glucose import GlucoseCreate, GlucoseUpdate
from sqlalchemy import and_
from datetime import datetime

class CRUDGlucose:
    async def create(
        self, db: AsyncSession, *, obj_in: GlucoseCreate, user_id: int
    ) -> Glucose:
        db_obj = Glucose(
            user_id=user_id,
            glucose_value=obj_in.glucose_value,
            glucose_date=obj_in.glucose_date,
            measurement_type=obj_in.measurement_type,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(self, db: AsyncSession, id: int) -> Optional[Glucose]:
        query = select(Glucose).where(Glucose.id == id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi_by_user(
        self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Glucose]:
        query = select(Glucose)\
            .where(Glucose.user_id == user_id)\
            .offset(skip)\
            .limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def update(
        self, db: AsyncSession, *, db_obj: Glucose, obj_in: GlucoseUpdate
    ) -> Glucose:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> Glucose:
        query = select(Glucose).where(Glucose.id == id)
        result = await db.execute(query)
        obj = result.scalar_one_or_none()
        if obj:
            await db.delete(obj)
            await db.commit()
        return 
    
    async def get_user_records_by_date_range(
        self,
        db: AsyncSession,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[Glucose]:
        """
        Get user's glucose records within a date range.
        """
        query = select(Glucose).where(
            and_(
                Glucose.user_id == user_id,
                Glucose.glucose_date >= start_date,
                Glucose.glucose_date <= end_date
            )
        ).order_by(Glucose.glucose_date.asc())
        
        result = await db.execute(query)
        return result.scalars().all()

glucose = CRUDGlucose() 


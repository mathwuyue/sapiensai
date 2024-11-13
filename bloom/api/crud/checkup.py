from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date

from ..models.checkup import Checkup
from ..schemas.checkup import CheckupCreate, CheckupUpdate
from .base import CRUDBase

class CRUDCheckup(CRUDBase[Checkup, CheckupCreate, CheckupUpdate]):
    async def get_by_user_id(
        self, db: AsyncSession, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[Checkup]:
        query = select(Checkup).where(Checkup.user_id == user_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_date_range(
        self, 
        db: AsyncSession, 
        *, 
        user_id: str,
        start_date: date,
        end_date: date
    ) -> List[Checkup]:
        query = select(Checkup).where(
            Checkup.user_id == user_id,
            Checkup.checkup_date >= start_date,
            Checkup.checkup_date <= end_date
        )
        result = await db.execute(query)
        return result.scalars().all()

checkup = CRUDCheckup(Checkup) 
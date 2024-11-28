from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.prenatal_screening import PrenatalScreening
from ..schemas.prenatal_screening import PrenatalScreeningCreate, PrenatalScreeningUpdate
from .base import CRUDBase

class CRUDPrenatalScreening(CRUDBase[PrenatalScreening, PrenatalScreeningCreate, PrenatalScreeningUpdate]):
    async def get_by_checkup_id(
        self, db: AsyncSession, *, checkup_id: int
    ) -> List[PrenatalScreening]:
        query = select(PrenatalScreening).where(PrenatalScreening.checkup_id == checkup_id)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_screening_type(
        self, db: AsyncSession, *, user_id: str, screening_type: str
    ) -> List[PrenatalScreening]:
        query = (
            select(PrenatalScreening)
            .join(PrenatalScreening.checkup)
            .where(
                PrenatalScreening.screening_type == screening_type,
                PrenatalScreening.checkup.has(user_id=user_id)
            )
        )
        result = await db.execute(query)
        return result.scalars().all()

prenatal_screening = CRUDPrenatalScreening(PrenatalScreening) 
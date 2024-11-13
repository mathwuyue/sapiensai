from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.ultrasound import Ultrasound
from ..schemas.ultrasound import UltrasoundCreate, UltrasoundUpdate
from .base import CRUDBase

class CRUDUltrasound(CRUDBase[Ultrasound, UltrasoundCreate, UltrasoundUpdate]):
    async def get_by_checkup_id(self, db: AsyncSession, *, checkup_id: int) -> Optional[Ultrasound]:
        query = select(Ultrasound).where(Ultrasound.checkup_id == checkup_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

ultrasound = CRUDUltrasound(Ultrasound) 
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.vital_signs import VitalSigns
from ..schemas.vital_signs import VitalSignsCreate, VitalSignsUpdate
from .base import CRUDBase

class CRUDVitalSigns(CRUDBase[VitalSigns, VitalSignsCreate, VitalSignsUpdate]):
    async def get_by_checkup_id(self, db: AsyncSession, *, checkup_id: int) -> Optional[VitalSigns]:
        query = select(VitalSigns).where(VitalSigns.checkup_id == checkup_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

vital_signs = CRUDVitalSigns(VitalSigns) 
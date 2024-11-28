from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.lab_results import LabResults
from ..schemas.lab_results import LabResultsCreate, LabResultsUpdate
from .base import CRUDBase

class CRUDLabResults(CRUDBase[LabResults, LabResultsCreate, LabResultsUpdate]):
    async def get_by_checkup_id(self, db: AsyncSession, *, checkup_id: int) -> Optional[LabResults]:
        query = select(LabResults).where(LabResults.checkup_id == checkup_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

lab_results = CRUDLabResults(LabResults) 
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.patient import Patient
from ..schemas.patient import PatientCreate, PatientUpdate
from .base import CRUDBase

class CRUDPatient(CRUDBase[Patient, PatientCreate, PatientUpdate]):
    async def get_by_user_id(self, db: AsyncSession, *, user_id: str) -> Optional[Patient]:
        query = select(Patient).where(Patient.user_id == user_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

patient = CRUDPatient(Patient) 
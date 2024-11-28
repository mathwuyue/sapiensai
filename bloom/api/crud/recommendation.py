from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date

from ..models.recommendation import Recommendation
from ..schemas.recommendation import RecommendationCreate, RecommendationUpdate
from .base import CRUDBase

class CRUDRecommendation(CRUDBase[Recommendation, RecommendationCreate, RecommendationUpdate]):
    async def get_by_checkup_id(
        self, db: AsyncSession, *, checkup_id: int
    ) -> List[Recommendation]:
        query = select(Recommendation).where(Recommendation.checkup_id == checkup_id)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_active_recommendations(
        self, db: AsyncSession, *, user_id: str, current_date: date = None
    ) -> List[Recommendation]:
        if current_date is None:
            current_date = date.today()
        
        query = (
            select(Recommendation)
            .join(Recommendation.checkup)
            .where(
                Recommendation.checkup.has(user_id=user_id),
                (Recommendation.valid_until >= current_date) | (Recommendation.valid_until.is_(None))
            )
        )
        result = await db.execute(query)
        return result.scalars().all()

recommendation = CRUDRecommendation(Recommendation) 
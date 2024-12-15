from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

#from api.database import get_db
from api.models.exercise import Exercise
from api.schemas.exercise import ExerciseResponse # 需要创建
from api.core.dependencies import get_db, get_current_user
from api.models.user import User
router = APIRouter()

@router.get("/emma/exercise", response_model=List[ExerciseResponse])
async def get_user_exercises(
    #之后看看需不需要*
    # user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    start_date: datetime = None,
    end_date: datetime = None
):
    print("router.get",router)
    # query = db.query(Exercise).filter(Exercise.user_id == current_user.id)
    # if start_date:
    #     query = query.filter(Exercise.start_time >= start_date)
    # if end_date:
    #     query = query.filter(Exercise.start_time <= end_date)
        
    # return query.order_by(Exercise.start_time.desc()).all()
    exercises = db.query(Exercise)\
        .filter(Exercise.user_id == current_user.id)\
        .order_by(Exercise.start_time.desc())\
        .all()
    
    return exercises
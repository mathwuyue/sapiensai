from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

#from api.database import get_db
from api.models.exercise import Exercise
from api.schemas.exercise import ExerciseResponse # 需要创建
from api.core.dependencies import get_db, get_current_user
from api.models.user import User
from api.crud.exercise import exercise
from sqlalchemy.ext.asyncio import AsyncSession
from api.schemas.exercise import ExerciseCreate
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import json
from sqlalchemy import select, update
router = APIRouter()

# api/routes/v1/exercise.py
# @router.put("/{exercise_id}/feedback")
# async def update_exercise_feedback(
#     exercise_id: int,
#     feedback: dict,  # 包含 summary 和 advice
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ) -> ExerciseResponse:  # 明确指定返回类型
#     exercise_record = await exercise.get(db=db, id=exercise_id)
#     if not exercise_record:
#         raise HTTPException(status_code=404, detail="Exercise record not found")
    
#     # 更新 feedback
#     updated_record = await exercise.update(
#         db=db,
#         db_obj=exercise_record,
#         obj_in={
#             "summary": feedback.get("summary"),
#             "advice": feedback.get("advice")
#         }
#     )
    
#     return updated_record

# @router.put("/{exercise_id}/feedback")
# async def update_exercise_feedback(
#     id: int,
#     summary: str,
#     advice: str,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ) -> ExerciseResponse:
#     print(f"Received feedback request: {feedback}")  # 调试日志

#     updated_exercise = await exercise.update_exercise_feedback(
#         db=db,
#         exercise_id=id,
#         summary=summary,
#         advice=advice
#     )
    
#     if not updated_exercise:
#         raise HTTPException(status_code=404, detail="Exercise record not found")
        
#     return updated_exercise
   

@router.get("/", response_model=List[ExerciseResponse])
async def get_user_exercises(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve exercise records for current user.
    """
    exercises = await exercise.get_multi_by_user(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return list(exercises)

@router.delete("/{exercise_id}")
async def delete_exercise(
    exercise_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 添加用户认证
) -> dict:
    try:
        deleted = await exercise.remove(db=db, exercise_id=exercise_id)
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Exercise not found"
            )
        return {
            "status": "success",
            "message": "Exercise deleted",
            "id": exercise_id
        }
    except Exception as e:
        print(f"Error deleting exercise: {str(e)}")  # 添加日志
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from serve.db import UploadFile, User, db
import dotenv
from llm import llm, chunk_to_dict
from serve.model import DietaryResponse, NutritionResponse
import time
from pathlib import Path
from pydantic import BaseModel
from typing import Dict, Any, Optional
from serve.model import ExerciseDataRequest
from storage.oss import get_file as oss_get_file
from storage.local import get_file as local_get_file
from nutrition.model import NutritionMacro, NutritionMicro, NutritionMineral
from prompt import get_food_nutrients_prompt
from nutrition.db import ExerciseData, ExerciseDatabase
from nutrition.emma import dietary_recommendation, get_exercise_summary


dotenv.load_dotenv()
router = APIRouter()


class UserInfoRequest(BaseModel):
    user_id: str


# @router.post("/v1/emma/dietary")
# async def get_dietary_recommendation(request: UserInfoRequest) -> DietaryResponse:
#     try:
#         result = await dietary_recommendation(basicinfo={}, glu=[], meals=[], orig_plan="")
#         return DietaryResponse(
#             status=200,
#             resp={
#                 "message": "Successfully generated dietary recommendations",
#                 "data": result
#             }
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Failed to generate dietary recommendations: {str(e)}"
#         )


@router.post("/v1/emma/exercise")
async def save_exercise_data(request: ExerciseDataRequest):
    exercise = ExerciseData.create(
        user_id=request.user_id,
        exercise=request.exercise,
        duration=request.duration,
        intensity=request.intensity,
        bpm=request.bpm,
        remark=request.remark,
        start_time=request.start_time,
        calories=0.0,  # Default value, could be calculated based on exercise type
        updated_at=datetime.now()
    )
    try:
        # get emma comment
        emma_comment, calories = await get_exercise_summary(request.user_id, request.exercise, request.intensity, request.duration, request.bpm, request.start_time, request.remark)
        exercise.calories = calories
        exercise.emma = emma_comment.model_dump_json()
        exercise.save()
        return {
            "status": 200,
            "summary": emma_comment.summary,
            "advice": emma_comment.advice,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save exercise data: {str(e)}"
        )


def init_app(app):
    app.include_router(router)
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from serve.db import UploadFile, User, db
import dotenv
from llm import llm, chunk_to_dict
from serve.model import DietaryResponse, NutritionResponse
import traceback
from pathlib import Path
from pydantic import BaseModel
from typing import Dict, Any, Optional
import base64
from storage.huawei import get_file as hw_get_file
from storage.local import get_file as local_get_file
from nutrition.model import NutritionMacro, NutritionMicro, NutritionMineral
from prompt import get_food_nutrients_prompt
from nutrition.db import MealData, ExerciseData
from nutrition.emma import analyze_food

dotenv.load_dotenv()
router = APIRouter()


class UserInfoRequest(BaseModel):
    user_id: str


class FoodRequest(BaseModel):
    user_id: str
    url: str
    type: int
    storage: Optional[str] = None
    

class ExerciseRequest(BaseModel):
    user_id: str
    exercise: str
    duration: float
    start_time: Optional[datetime] = None


@router.post("/v1/userinfo/basicinfo")
async def create_basic_info(request: UserInfoRequest) -> Dict[str, Any]:
    try:
        with db.atomic():
            user = User.create(
                userid=request.user_id,
                user_meta={},
                updated_at=datetime.now()
            )
            return {
                "status": 200,
                "resp": {"user_id": user.userid}
            }
    except Exception as e:
        if "unique constraint" in str(e).lower():
            raise HTTPException(
                status_code=400,
                detail="User ID already exists"
            )
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/v1/userinfo/food")
async def process_food_image(request: FoodRequest) -> NutritionResponse:
    try:
        # Get file from storage
        if not request.storage:
            file_data = hw_get_file(request.url)
        elif request.storage == 'local':
            file_data = local_get_file(request.url)
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid storage type"
            )
        # Convert to base64
        image_base64 = base64.b64encode(file_data).decode('utf-8')
        # Analyze food image
        nutrition_info = await analyze_food(image_base64)
        # Save food data to MealData table
        meal = MealData.create(
            userid=request.user_id,
            type=request.type,
            url={'url': request.url, 'storage': request.storage},
            nutrient={
                'macro': nutrition_info[0].model_dump(),
                'micro': nutrition_info[1].model_dump(),
                'mineral': nutrition_info[2].model_dump()
            },
            updated_at=datetime.now()
        )
        return NutritionResponse(macro=nutrition_info[0], micro=nutrition_info[1], mineral=nutrition_info[2])
    except HTTPException:
        raise
    except Exception as e:
        traceback_str = ''.join(traceback.format_exc())
        print(f"Exception occurred: {traceback_str}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/v1/userinfo/exercise")
async def process_exercise(request: ExerciseRequest) -> dict:
    try:
        with db.atomic():
            exercise = ExerciseData.create(
                user_id=request.user_id,
                exercise=request.exercise,
                duration=request.duration,
                start_time=request.start_time,
                calories=0.0,  # Default value, can be calculated later if needed
                updated_at=datetime.now()
            )
            return {
                "status": 200,
                "resp": {
                    "id": exercise.id,
                    "user_id": exercise.user_id,
                    "exercise": exercise.exercise,
                    "duration": exercise.duration,
                    "start_time": exercise.start_time
                }
            }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )
        
        
def get_meal_data(user_id: str, date: datetime, offset: int) -> list[MealData]:
    meals = MealData.select().where(MealData.userid == user_id)
    return meals


def get_user_info(user_id: str) -> User:
    user = User.get(User.userid == user_id)
    return user

def get_

def init_app(app):
    app.include_router(router)
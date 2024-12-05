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
import base64
from storage.huawei import get_file as hw_get_file
from storage.local import get_file as local_get_file
from nutrition.model import NutritionMacro, NutritionMicro, NutritionMineral
from prompt import get_food_nutrients_prompt
from nutrition.db import ExerciseData
from nutrition.emma import dietary_recommendation


dotenv.load_dotenv()
router = APIRouter()


class UserInfoRequest(BaseModel):
    user_id: str


@router.post("/v1/emma/dietary")
def get_dietary_recommendation(request: UserInfoRequest) -> DietaryResponse:
    try:
        result = await dietary_recommendation(basicinfo={}, glu=[], meals=[], orig_plan="")
        return DietaryResponse(
            status=200,
            resp={
                "message": "Successfully generated dietary recommendations",
                "data": result
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate dietary recommendations: {str(e)}"
        )


def init_app(app):
    app.include_router(router)
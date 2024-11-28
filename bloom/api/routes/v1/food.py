from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
import base64
import io

from api import crud, models, schemas
from api.core.dependencies import get_db, get_current_user
from api.services.openai_service import analyze_food_image

router = APIRouter()

@router.post("/analyze", response_model=schemas.FoodAnalysis)
async def analyze_food(
    *,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    # current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Analyze food image and return calorie information
    """
    try:
        # Read image file
        contents = await file.read()
        
        # Convert to base64 for OpenAI API
        base64_image = base64.b64encode(contents).decode('utf-8')
        
        # Get analysis from OpenAI
        analysis = await analyze_food_image(base64_image)
        
        # Save analysis to database if needed
        # food_record = await crud.food_record.create(...)
        
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to analyze food image: {str(e)}"
        ) 
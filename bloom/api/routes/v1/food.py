from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, List
import base64
import logging
import os
from datetime import datetime
import aiofiles
from api.models.user import User
from api.core.config import settings
from api import crud, models, schemas
from api.core.dependencies import get_db, get_current_user
from api.services.openai_service import analyze_food_image
from api.schemas.food import FoodAnalyze, FoodAnalyzeCreate

router = APIRouter()
logger = logging.getLogger(__name__)

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

async def save_upload_file(file: UploadFile, contents: bytes) -> str:
    """Save uploaded file and return file path"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_name = file.filename or "unnamed"
    filename = f"{timestamp}_{original_name}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    async with aiofiles.open(file_path, 'wb') as out_file:
        await out_file.write(contents)
    
    return file_path

@router.post("/analyze", response_model=FoodAnalyze)
async def analyze_food(
    *,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Analyze food image and save results to database"""
    file_path = None
    
    try:
        logger.debug(f"Received file: {file.filename}, content_type: {file.content_type}")
        
        # 1. 读取文件并保存
        contents = await file.read()
        file_path = await save_upload_file(file, contents)
        logger.info(f"File saved to: {file_path}")
        
        # 2. 准备图片数据并进行 AI 分析
        base64_image = base64.b64encode(contents).decode('utf-8')
        analysis_result = await analyze_food_image(base64_image)
        
        # 3. 准备数据库对象
        food_analysis = FoodAnalyzeCreate(
            file_path=file_path,
            original_filename=file.filename,
            content_type=file.content_type,
            **analysis_result.model_dump()
        )
        
        # 4. 使用事务处理数据库操作
        db_obj = await crud.food.create_with_user(
            db=db,
            obj_in=food_analysis,
            user_id=current_user.id
        )
        await db.commit()
        await db.refresh(db_obj)
        return db_obj.to_schema()

    except Exception as e:
        await db.rollback()
        logger.error(f"Error processing file: {str(e)}")
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to analyze food image: {str(e)}"
        )

@router.get("/analyses", response_model=List[FoodAnalyze])
async def get_food_analyses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 10,
) -> Any:
    """Get list of food analyses for current user"""
    analyses = await crud.food.get_multi_by_user(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return [analysis.to_schema() for analysis in analyses]

@router.get("/analyses/{analysis_id}", response_model=FoodAnalyze)
async def get_food_analysis(
    analysis_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get specific food analysis by ID"""
    analysis = await crud.food.get_by_id_and_user(
        db=db,
        id=analysis_id,
        user_id=current_user.id
    )
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Food analysis not found"
        )
    return analysis.to_schema()
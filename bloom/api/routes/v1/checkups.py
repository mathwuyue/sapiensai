from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from api import crud, models, schemas
from api.deps import get_current_patient, verify_checkup_access
from api.core.dependencies import get_db, get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.Checkup)
async def create_checkup(
    *,
    db: AsyncSession = Depends(get_db),
    checkup_in: schemas.CheckupCreate,
    patient: models.Patient = Depends(get_current_patient),
) -> Any:
    """
    Create new checkup record.
    Requires patient profile to exist.
    """
    checkup = await crud.checkup.create(db, obj_in=checkup_in)
    return checkup

@router.get("/", response_model=List[schemas.Checkup])
async def read_checkups(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Retrieve all checkups for the current user.
    """
    checkups = await crud.checkup.get_by_user_id(
        db, user_id=current_user.user_id, skip=skip, limit=limit
    )
    return checkups

@router.get("/{checkup_id}", response_model=schemas.Checkup)
async def read_checkup(
    *,
    checkup: models.Checkup = Depends(verify_checkup_access),
) -> Any:
    """
    Get specific checkup by ID.
    Verifies user has access to the checkup.
    """
    return checkup

@router.put("/{checkup_id}", response_model=schemas.Checkup)
async def update_checkup(
    *,
    db: AsyncSession = Depends(get_db),
    checkup: models.Checkup = Depends(verify_checkup_access),
    checkup_in: schemas.CheckupUpdate,
) -> Any:
    """
    Update a checkup record.
    Verifies user has access to the checkup.
    """
    updated_checkup = await crud.checkup.update(db, db_obj=checkup, obj_in=checkup_in)
    return updated_checkup 
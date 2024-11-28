from typing import Generator
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.core.dependencies import get_current_user, get_db
from api import crud, models

async def get_current_patient(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> models.Patient:
    """
    Get current user's patient profile.
    This is a specific dependency for the maternal health system.
    """
    patient = await crud.patient.get_by_user_id(db, user_id=current_user.user_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    return patient

async def verify_checkup_access(
    checkup_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> models.Checkup:
    """
    Verify if the current user has access to a specific checkup record.
    Raises 404 if checkup not found or 403 if user doesn't have permission.
    """
    checkup = await crud.checkup.get(db, id=checkup_id)
    if not checkup:
        raise HTTPException(status_code=404, detail="Checkup not found")
    if checkup.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return checkup

async def verify_medical_record_access(
    checkup_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> models.Checkup:
    """
    Verify if the current user has access to medical records of a specific checkup.
    This is used for vital signs, ultrasound, lab results, etc.
    """
    checkup = await crud.checkup.get(db, id=checkup_id)
    if not checkup or checkup.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Checkup not found")
    return checkup
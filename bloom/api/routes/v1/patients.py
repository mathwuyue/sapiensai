from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api import crud, models, schemas
from api.deps import get_current_patient
from api.core.dependencies import get_db, get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.Patient)
async def create_patient(
    *,
    db: AsyncSession = Depends(get_db),
    patient_in: schemas.PatientCreate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Create new patient profile.
    Verifies no existing profile exists for the user.
    """
    patient = await crud.patient.get_by_user_id(db, user_id=current_user.user_id)
    if patient:
        raise HTTPException(
            status_code=400,
            detail="Patient profile already exists for this user",
        )
    patient_in.user_id = current_user.user_id
    patient = await crud.patient.create(db, obj_in=patient_in)
    return patient

@router.get("/me", response_model=schemas.Patient)
async def read_patient_me(
    patient: models.Patient = Depends(get_current_patient),
) -> Any:
    """
    Get current user's patient profile.
    """
    return patient

@router.put("/me", response_model=schemas.Patient)
async def update_patient_me(
    *,
    db: AsyncSession = Depends(get_db),
    patient: models.Patient = Depends(get_current_patient),
    patient_in: schemas.PatientUpdate,
) -> Any:
    """
    Update current user's patient profile.
    """
    updated_patient = await crud.patient.update(db, db_obj=patient, obj_in=patient_in)
    return updated_patient 
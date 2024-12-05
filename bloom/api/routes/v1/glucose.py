from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from api.core.dependencies import get_current_user, get_db, verify_admin_token
from api.crud.glucose import glucose
from api.schemas.glucose import Glucose, GlucoseCreate, GlucoseUpdate, GlucoseReadingResponse, GlucoseListResponse
from api.models.user import User
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()

@router.post("/", response_model=List[Glucose])
async def create_glucose(
    *,
    db: AsyncSession = Depends(get_db),
    glucose_in: List[GlucoseCreate],
    current_user: User = Depends(get_current_user)
):
    """
    Create new glucose record.
    """
    glucose_record = []
    for glucose_reading in glucose_in:
        record = await glucose.create(db, obj_in=glucose_reading, user_id=current_user.id)
        glucose_record.append(record)
    return glucose_record

@router.get("/", response_model=List[Glucose])
async def read_glucoses(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve glucose records.
    """
    glucoses = await glucose.get_multi_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return glucoses

@router.get("/{glucose_id}", response_model=Glucose)
async def read_glucose(
    *,
    db: AsyncSession = Depends(get_db),
    glucose_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Get glucose record by ID.
    """
    glucose_record = await glucose.get(db, id=glucose_id)
    if not glucose_record:
        raise HTTPException(status_code=404, detail="Glucose record not found")
    if glucose_record.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return glucose_record

@router.put("/{glucose_id}", response_model=Glucose)
async def update_glucose(
    *,
    db: AsyncSession = Depends(get_db),
    glucose_id: int,
    glucose_in: GlucoseUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update glucose record.
    """
    glucose_record = await glucose.get(db, id=glucose_id)
    if not glucose_record:
        raise HTTPException(status_code=404, detail="Glucose record not found")
    if glucose_record.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    glucose_record = await glucose.update(db, db_obj=glucose_record, obj_in=glucose_in)
    return glucose_record

@router.delete("/{glucose_id}", response_model=Glucose)
async def delete_glucose(
    *,
    db: AsyncSession = Depends(get_db),
    glucose_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Delete glucose record.
    """
    glucose_record = await glucose.get(db, id=glucose_id)
    if not glucose_record:
        raise HTTPException(status_code=404, detail="Glucose record not found")
    if glucose_record.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    glucose_record = await glucose.remove(db, id=glucose_id)
    return glucose_record

@router.get("/user/{user_id}", response_model=GlucoseListResponse)
async def read_user_glucose(
    *,
    db: AsyncSession = Depends(get_db),
    user_id: int,
    date: Optional[datetime] = None,
    offset: Optional[int] = 0,
    _: str = Depends(verify_admin_token)
) -> GlucoseListResponse:
    """
    Get glucose records for a specific user.
    Requires valid admin token in Authorization header.
    """
    # if no date provided, use current date
    if date is None:
        date = datetime.now()

    # calculate date range
    end_date = date.replace(hour=23, minute=59, second=59)
    if offset > 0:
        start_date = (date - timedelta(days=offset)).replace(hour=0, minute=0, second=0)
    else:
        start_date = date.replace(hour=0, minute=0, second=0)

    # get glucose records within date range
    glucose_records = await glucose.get_user_records_by_date_range(
        db=db,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date
    )

    # convert to response format
    readings = [
        GlucoseReadingResponse(
            datetime=record.glucose_date,
            glu=record.glucose_value,
            type=record.measurement_type
        ) for record in glucose_records
    ]

    return GlucoseListResponse(
        total=len(readings),
        data=readings
    )
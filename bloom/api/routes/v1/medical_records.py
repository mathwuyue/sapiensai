from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession

from api import crud, models, schemas
from api.core.dependencies import get_db, get_current_user
from api.deps import verify_medical_record_access

router = APIRouter()

# Vital Signs endpoints
@router.post("/vital-signs/{checkup_id}", response_model=schemas.VitalSigns)
async def create_vital_signs(
    *,
    checkup_id: int = Path(..., title="The ID of the checkup"),
    db: AsyncSession = Depends(get_db),
    vital_signs_in: schemas.VitalSignsCreate,
    checkup: models.Checkup = Depends(verify_medical_record_access),
) -> Any:
    """
    Create new vital signs record.
    """
    vital_signs = await crud.vital_signs.create(db, obj_in=vital_signs_in)
    return vital_signs

@router.get("/vital-signs/{checkup_id}", response_model=schemas.VitalSigns)
async def read_vital_signs(
    checkup_id: int = Path(..., title="The ID of the checkup"),
    db: AsyncSession = Depends(get_db),
    checkup: models.Checkup = Depends(verify_medical_record_access),
) -> Any:
    """
    Get vital signs for a specific checkup.
    """
    vital_signs = await crud.vital_signs.get_by_checkup_id(db, checkup_id=checkup_id)
    if not vital_signs:
        raise HTTPException(status_code=404, detail="Vital signs not found")
    return vital_signs

# Ultrasound endpoints
@router.post("/ultrasound/{checkup_id}", response_model=schemas.Ultrasound)
async def create_ultrasound(
    *,
    checkup_id: int = Path(..., title="The ID of the checkup"),
    db: AsyncSession = Depends(get_db),
    ultrasound_in: schemas.UltrasoundCreate,
    checkup: models.Checkup = Depends(verify_medical_record_access),
) -> Any:
    """
    Create new ultrasound record.
    """
    ultrasound = await crud.ultrasound.create(db, obj_in=ultrasound_in)
    return ultrasound

@router.get("/ultrasound/{checkup_id}", response_model=schemas.Ultrasound)
async def read_ultrasound(
    checkup_id: int = Path(..., title="The ID of the checkup"),
    db: AsyncSession = Depends(get_db),
    checkup: models.Checkup = Depends(verify_medical_record_access),
) -> Any:
    """
    Get ultrasound record for a specific checkup.
    """
    ultrasound = await crud.ultrasound.get_by_checkup_id(db, checkup_id=checkup_id)
    if not ultrasound:
        raise HTTPException(status_code=404, detail="Ultrasound record not found")
    return ultrasound

# Lab Results endpoints
@router.post("/lab-results", response_model=schemas.LabResults)
async def create_lab_results(
    *,
    db: AsyncSession = Depends(get_db),
    lab_results_in: schemas.LabResultsCreate,
    current_user: schemas.User = Depends(get_current_user),
) -> Any:
    """
    Create new lab results record.
    """
    checkup = await crud.checkup.get(db, id=lab_results_in.checkup_id)
    if not checkup or checkup.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Checkup not found")
    lab_results = await crud.lab_results.create(db, obj_in=lab_results_in)
    return lab_results

@router.get("/lab-results/{checkup_id}", response_model=schemas.LabResults)
async def read_lab_results(
    *,
    db: AsyncSession = Depends(get_db),
    checkup_id: int,
    current_user: schemas.User = Depends(get_current_user),
) -> Any:
    """
    Get lab results for a specific checkup.
    """
    lab_results = await crud.lab_results.get_by_checkup_id(db, checkup_id=checkup_id)
    if not lab_results:
        raise HTTPException(status_code=404, detail="Lab results not found")
    if (await crud.checkup.get(db, id=checkup_id)).user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return lab_results

# Prenatal Screening endpoints
@router.post("/prenatal-screenings", response_model=schemas.PrenatalScreening)
async def create_prenatal_screening(
    *,
    db: AsyncSession = Depends(get_db),
    screening_in: schemas.PrenatalScreeningCreate,
    _: models.Checkup = Depends(verify_medical_record_access),
) -> Any:
    """
    Create new prenatal screening record.
    Verifies user has access to the associated checkup.
    """
    screening = await crud.prenatal_screening.create(db, obj_in=screening_in)
    return screening

@router.get("/prenatal-screenings/{checkup_id}", response_model=List[schemas.PrenatalScreening])
async def read_prenatal_screenings(
    *,
    checkup: models.Checkup = Depends(verify_medical_record_access),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get all prenatal screenings for a specific checkup.
    """
    screenings = await crud.prenatal_screening.get_by_checkup_id(db, checkup_id=checkup.id)
    return screenings

# Recommendations endpoints
@router.post("/recommendations", response_model=schemas.Recommendation)
async def create_recommendation(
    *,
    db: AsyncSession = Depends(get_db),
    recommendation_in: schemas.RecommendationCreate,
    _: models.Checkup = Depends(verify_medical_record_access),
) -> Any:
    """
    Create new recommendation.
    Verifies user has access to the associated checkup.
    """
    recommendation = await crud.recommendation.create(db, obj_in=recommendation_in)
    return recommendation

@router.get("/recommendations/active", response_model=List[schemas.Recommendation])
async def read_active_recommendations(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Get all active recommendations for the current user.
    """
    recommendations = await crud.recommendation.get_active_recommendations(
        db, user_id=current_user.user_id
    )
    return recommendations 
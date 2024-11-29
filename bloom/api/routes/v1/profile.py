from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request
from pydantic import ValidationError
from api.deps import get_current_user, get_db
from api.crud import profile as profile_crud
from api.schemas.profile import (
    Profile, ProfileCreate, ProfileUpdate, ProfileBasicInfo,
    PresetCondition, PresetComplication, ProfileAdminView
)
from api.models.user import User
from api.core.dependencies import verify_admin_token

router = APIRouter()

async def log_request(request: Request):
    body = await request.json()
    print("\n=== Raw Request Data ===")
    print("Request Body:", body)
    print("======================\n")
    return body

@router.post("/", response_model=Profile)
async def create_profile(
    *,
    db: AsyncSession = Depends(get_db),
    profile_in: ProfileCreate,
    current_user: User = Depends(get_current_user),
    raw_data: dict = Depends(log_request)
) -> Profile:
    """
    Create new profile for current user.
    """
    
    # Check if user already has a profile
    existing_profile = await profile_crud.get_profile_by_user(db, user_id=current_user.id)
    if existing_profile:
        return await profile_crud.update_profile(db, db_profile=existing_profile, profile_update=profile_in)
    
    return await profile_crud.create_profile(db, profile=profile_in, user_id=current_user.id)

@router.get("/me", response_model=Profile)
async def read_user_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Profile:
    """
    Get current user's profile.
    """
    user_profile = await profile_crud.get_profile_by_user(db, user_id=current_user.id)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return user_profile

@router.put("/me", response_model=Profile)
async def update_user_profile(
    *,
    db: AsyncSession = Depends(get_db),
    profile_in: ProfileUpdate,
    current_user: User = Depends(get_current_user)
) -> Profile:
    """
    Update current user's profile.
    """
    user_profile = await profile_crud.get_profile_by_user(db, user_id=current_user.id)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return await profile_crud.update_profile(db, db_profile=user_profile, profile_update=profile_in)

@router.delete("/me", response_model=Profile)
async def delete_user_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Profile:
    """
    Delete current user's profile.
    """
    user_profile = await profile_crud.get_profile_by_user(db, user_id=current_user.id)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    deleted = await profile_crud.delete_profile(db, profile_id=user_profile.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete profile"
        )
    return user_profile

@router.get("/{profile_id}", response_model=Profile)
async def read_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Profile:
    """
    Get profile by ID.
    Only superusers can access other users' profiles.
    """
    profile = await profile_crud.get_profile(db, profile_id=profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    if not current_user.is_superuser and profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return profile

@router.get("/", response_model=List[Profile])
async def list_profiles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
) -> List[Profile]:
    """
    List all profiles.
    Only superusers can access this endpoint.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return await profile_crud.get_profiles(db, skip=skip, limit=limit)

# Preset Conditions endpoints
@router.get("/conditions/preset", response_model=List[PresetCondition])
async def list_preset_conditions(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> List[PresetCondition]:
    """
    List all active preset conditions.
    """
    return await profile_crud.get_preset_conditions(db, skip=skip, limit=limit)

@router.get("/conditions/preset/{condition_id}", response_model=PresetCondition)
async def read_preset_condition(
    condition_id: int,
    db: AsyncSession = Depends(get_db)
) -> PresetCondition:
    """
    Get preset condition by ID.
    """
    condition = await profile_crud.get_preset_condition(db, condition_id=condition_id)
    if not condition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preset condition not found"
        )
    return condition

# Preset Complications endpoints
@router.get("/complications/preset", response_model=List[PresetComplication])
async def list_preset_complications(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> List[PresetComplication]:
    """
    List all active preset complications.
    """
    return await profile_crud.get_preset_complications(db, skip=skip, limit=limit)

@router.get("/complications/preset/{complication_id}", response_model=PresetComplication)
async def read_preset_complication(
    complication_id: int,
    db: AsyncSession = Depends(get_db)
) -> PresetComplication:
    """
    Get preset complication by ID.
    """
    complication = await profile_crud.get_preset_complication(db, complication_id=complication_id)
    if not complication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preset complication not found"
        )
    return complication

@router.get("/user/{user_id}", response_model=ProfileAdminView)
async def read_user_profile_by_admin(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_admin_token)
) -> ProfileAdminView:
    """
    Get a user's profile by user ID.
    Requires valid admin token in Authorization header.
    """
    user_profile = await profile_crud.get_profile_by_user(db, user_id=user_id)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile not found for user {user_id}"
        )
    
    return ProfileAdminView.from_profile(user_profile)
  
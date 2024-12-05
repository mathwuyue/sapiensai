from typing import List, Optional, Union, Dict, Any
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from api.models.profile import Profile, PresetCondition, UserCondition, PresetComplication, UserComplication
from api.schemas.profile import ProfileCreate, ProfileUpdate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import delete

async def get_profile(db: AsyncSession, profile_id: int) -> Optional[Profile]:
    """Get a profile by ID with all relationships loaded"""
    result = await db.execute(
        select(Profile)
        .options(
            selectinload(Profile.conditions).selectinload(UserCondition.preset_condition),
            selectinload(Profile.complications).selectinload(UserComplication.preset_complication)
        )
        .where(Profile.id == profile_id)
    )
    return result.scalars().first()

async def get_profile_by_user(db: AsyncSession, user_id: int) -> Optional[Profile]:
    """Get a profile by user ID with all relationships loaded"""
    result = await db.execute(
        select(Profile)
        .options(
            selectinload(Profile.conditions).selectinload(UserCondition.preset_condition),
            selectinload(Profile.complications).selectinload(UserComplication.preset_complication)
        )
        .where(Profile.user_id == user_id)
    )
    return result.scalars().first()

async def get_profiles(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100
) -> List[Profile]:
    """Get multiple profiles with pagination and relationships loaded"""
    result = await db.execute(
        select(Profile)
        .options(
            selectinload(Profile.conditions).selectinload(UserCondition.preset_condition),
            selectinload(Profile.complications).selectinload(UserComplication.preset_complication)
        )
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def create_profile(
    db: AsyncSession, 
    profile: ProfileCreate, 
    user_id: int
) -> Profile:
    """Create a new profile with conditions and complications"""
    # Extract conditions and complications from the profile data
    conditions = profile.conditions
    complications = profile.complications
    
    # Create profile without relationships
    profile_data = profile.dict(exclude={'conditions', 'complications'})
    print('profile_data', profile_data)
    db_profile = Profile(**profile_data, user_id=user_id)
    db.add(db_profile)
    await db.flush()  # Get the profile ID
    
    # Create conditions
    for condition in conditions:
        db_condition = UserCondition(
            profile_id=db_profile.id,
            preset_condition_id=condition.preset_condition_id,
            level=condition.level
        )
        db.add(db_condition)
    
    # Create complications
    for complication in complications:
        db_complication = UserComplication(
            profile_id=db_profile.id,
            preset_complication_id=complication.preset_complication_id
        )
        db.add(db_complication)
    
    await db.commit()
    await db.refresh(db_profile)
    return db_profile

async def update_profile(
    db: AsyncSession, 
    db_profile: Profile, 
    profile_update: ProfileUpdate
) -> Profile:
    """Update an existing profile"""
    # Convert profile_update to dict, excluding None values
    update_data = profile_update.dict(exclude_unset=True)
    
    # Handle conditions update if provided
    if 'conditions' in update_data:
        conditions = update_data.pop('conditions')
        # Remove existing conditions using DELETE statement
        await db.execute(
            delete(UserCondition).where(UserCondition.profile_id == db_profile.id)
        )
        
        # Add new conditions
        for condition in conditions:
            db_condition = UserCondition(
                profile_id=db_profile.id,
                preset_condition_id=condition['preset_condition_id'],
                level=condition['level']
            )
            db.add(db_condition)
    
    # Handle complications update if provided
    if 'complications' in update_data:
        complications = update_data.pop('complications')
        # Remove existing complications using DELETE statement
        await db.execute(
            delete(UserComplication).where(UserComplication.profile_id == db_profile.id)
        )
        
        # Add new complications
        for complication in complications:
            db_complication = UserComplication(
                profile_id=db_profile.id,
                preset_complication_id=complication['preset_complication_id']
            )
            db.add(db_complication)
    
    # Update profile attributes
    for field, value in update_data.items():
        setattr(db_profile, field, value)
    
    await db.commit()
    
    # refresh the profile to get the updated conditions and complications
    result = await db.execute(
        select(Profile)
        .options(
            selectinload(Profile.conditions).selectinload(UserCondition.preset_condition),
            selectinload(Profile.complications).selectinload(UserComplication.preset_complication)
        )
        .where(Profile.id == db_profile.id)
    )
    
    return result.scalars().first()

async def delete_profile(db: AsyncSession, profile_id: int) -> bool:
    """Delete a profile"""
    query = select(Profile).filter(Profile.id == profile_id)
    result = await db.execute(query)
    profile = result.scalar_one_or_none()
    
    if profile:
        await db.delete(profile)
        await db.commit()
        return True
    return False

# Preset Conditions CRUD
async def get_preset_conditions(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100
) -> List[PresetCondition]:
    """Get all active preset conditions"""
    query = select(PresetCondition)\
        .filter(PresetCondition.is_active == True)\
        .offset(skip)\
        .limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_preset_condition(
    db: AsyncSession, 
    condition_id: int
) -> Optional[PresetCondition]:
    """Get a preset condition by ID"""
    query = select(PresetCondition).filter(PresetCondition.id == condition_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

# Preset Complications CRUD
async def get_preset_complications(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100
) -> List[PresetComplication]:
    """Get all active preset complications"""
    query = select(PresetComplication)\
        .filter(PresetComplication.is_active == True)\
        .offset(skip)\
        .limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_preset_complication(
    db: AsyncSession, 
    complication_id: int
) -> Optional[PresetComplication]:
    """Get a preset complication by ID"""
    query = select(PresetComplication).filter(PresetComplication.id == complication_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

# User Conditions CRUD
async def update_profile_conditions(
    db: AsyncSession, 
    profile_id: int, 
    conditions: List[UserCondition]
) -> None:
    """Update profile conditions"""
    # Remove existing conditions
    query = select(UserCondition).filter(UserCondition.profile_id == profile_id)
    result = await db.execute(query)
    existing_conditions = result.scalars().all()
    for condition in existing_conditions:
        await db.delete(condition)
    
    # Add new conditions
    for condition in conditions:
        db_condition = UserCondition(
            profile_id=profile_id,
            preset_condition_id=condition.preset_condition_id,
            level=condition.level
        )
        db.add(db_condition)
    
    await db.commit()

# User Complications CRUD
async def update_profile_complications(
    db: AsyncSession, 
    profile_id: int, 
    complications: List[UserComplication]
) -> None:
    """Update profile complications"""
    # Remove existing complications
    query = select(UserComplication).filter(UserComplication.profile_id == profile_id)
    result = await db.execute(query)
    existing_complications = result.scalars().all()
    for complication in existing_complications:
        await db.delete(complication)
    
    # Add new complications
    for complication in complications:
        db_complication = UserComplication(
            profile_id=profile_id,
            preset_complication_id=complication.preset_complication_id
        )
        db.add(db_complication)
    
    await db.commit()
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api import crud, models, schemas
from api import deps
from ...core.security import get_password_hash

router = APIRouter()

@router.post("/", response_model=schemas.User)
async def create_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: schemas.UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = await crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = await crud.user.create(db, obj_in=user_in)
    return user

@router.get("/me", response_model=schemas.User)
async def read_user_me(
    current_user: schemas.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.put("/me", response_model=schemas.User)
async def update_user_me(
    *,
    db: AsyncSession = Depends(deps.get_db),
    password: str = None,
    email: str = None,
    current_user: schemas.User = Depends(deps.get_current_user),
) -> Any:
    """
    Update own user.
    """
    current_user_data = schemas.UserUpdate(**current_user.dict())
    if password is not None:
        current_user_data.password = password
    if email is not None:
        current_user_data.email = email
    user = await crud.user.update(db, db_obj=current_user, obj_in=current_user_data)
    return user
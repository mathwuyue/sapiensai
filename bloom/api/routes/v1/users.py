from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...db.session import get_db
from ...crud.user import user as user_crud
from ...schemas.user import UserCreate, User

router = APIRouter()

@router.post("/", response_model=User)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    # Check if user exists
    user = await user_crud.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists."
        )
    
    user = await user_crud.create(db, obj_in=user_in)
    return user

@router.get("/{email}")
async def get_user(email: str, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_by_email(db, email=email)
    return user
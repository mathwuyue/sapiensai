from typing import Generator, Optional, AsyncGenerator
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from contextlib import asynccontextmanager

from api.core.config import settings
from api.core.security import ALGORITHM
from api.db.session import async_session
from api import crud, models, schemas

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

# 修改数据库引擎配置
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    poolclass=NullPool,
    # asyncpg 特定的连接参数
    connect_args={
        "timeout": 60,  # 连接超时（秒）
    }
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    依赖函数：获取数据库会话
    增加了超时设置和错误处理
    """
    session = AsyncSession(
        engine,
        expire_on_commit=False,
    )
    try:
        # 设置会话级别的超时
        await session.execute(text("SET statement_timeout = '30000'"))  # 30 秒
        await session.execute(text("SET idle_in_transaction_session_timeout = '60000'"))  # 60 秒
        yield session
    finally:
        await session.close()

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> models.User:
    """
    Validates the access token and returns the current user.
    Raises HTTPException if token is invalid or user not found.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
        print(token_data)
        user_id = token_data.user_id
    except (jwt.JWTError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Returns the current user if active, raises HTTPException otherwise.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Returns the current user if superuser, raises HTTPException otherwise.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user

async def verify_admin_token(authorization: str = Header(...)):
    """
    Verify admin token from Authorization header.
    Can be used as a dependency in any endpoint that requires admin access.
    
    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(
            _: str = Depends(verify_admin_token)
        ):
            return {"message": "Admin access granted"}
    """
    try:
        # expect header format: "Bearer <token>"
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
        if token != settings.ADMIN_TOKEN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid admin token"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
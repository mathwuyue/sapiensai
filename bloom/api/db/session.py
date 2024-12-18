from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from api.core.config import settings
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

# 构建连接参数
connect_args = {
    "command_timeout": settings.POSTGRES_COMMAND_TIMEOUT,
    "timeout": settings.POSTGRES_CONNECT_TIMEOUT
}

engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=settings.SQLALCHEMY_POOL_SIZE,
    max_overflow=settings.SQLALCHEMY_MAX_OVERFLOW,
    pool_timeout=settings.SQLALCHEMY_POOL_TIMEOUT,
    pool_recycle=settings.SQLALCHEMY_POOL_RECYCLE,
    echo=settings.SQLALCHEMY_ECHO,
    connect_args=connect_args
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Dependency for FastAPI endpoints
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    session = async_session()
    logger.debug("Created new database session")
    try:
        yield session
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        try:
            await session.rollback()
        except Exception:
            pass  # 忽略回滚错误
        raise
    finally:
        try:
            await session.close()
        except Exception:
            pass  # 忽略关闭错误
        logger.debug("Database session closed")
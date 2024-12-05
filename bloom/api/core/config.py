from pydantic_settings import BaseSettings
from pydantic import computed_field
from functools import lru_cache
from pathlib import Path
from typing import List
class Settings(BaseSettings):
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Bloom"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days

    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",  # React default port
        "http://localhost:8000",  # FastAPI default port
        "http://127.0.0.1:8000",
        "http://54.201.31.205:8000",
        "http://54.201.31.205:3000",
        "http://54.201.31.205",
        "http://115.223.19.227",
        "http://115.223.19.227:3000",
        "http://115.223.19.227:8000",
    ]
    
    # Database settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str = "localhost"  # default value if not in .env
    POSTGRES_PORT: str = "5432"        # default value if not in .env
    POSTGRES_DB: str

    OPENAI_API_KEY: str
    QWEN_API_KEY: str

    ADMIN_TOKEN: str
    
    @computed_field
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = Path(__file__).parent.parent / ".env"
        print(env_file)

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
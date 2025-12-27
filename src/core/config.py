from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import validator
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Bangla Legal AI"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str
    QDRANT_URL: str
    QDRANT_API_KEY: Optional[str] = None
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @validator("QDRANT_URL")
    def validate_qdrant_url(cls, v):
        if not v:
            raise ValueError("QDRANT_URL cannot be empty")
        return v

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()

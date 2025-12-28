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
    
    # LLM Settings
    LLM_PROVIDER: str = "local" # "local" or "openai"
    OPENAI_API_KEY: Optional[str] = None
    
    # Local LLM Path
    LLM_MODEL_FILE: str = "models/Qwen2.5-1.5B-Instruct-GGUF.gguf"
    
    # OpenAI Settings
    LLM_MODEL_NAME: str = "gpt-4o"
    
    EMBEDDING_MODEL_PATH: str = "models/Finetuned Embedding Model.pkl"

    @validator("QDRANT_URL")
    def validate_qdrant_url(cls, v):
        if not v:
            raise ValueError("QDRANT_URL cannot be empty")
        return v

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()

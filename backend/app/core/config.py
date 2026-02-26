from pydantic_settings import BaseSettings
from typing import List
import secrets


class Settings(BaseSettings):
    PROJECT_NAME: str = "GIST Office Management System"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    DATABASE_URL: str
    
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    REDIS_URL: str = "redis://localhost:6379/0"
    
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: str | None = None
    EMAILS_FROM_NAME: str | None = None
    
    ENVIRONMENT: str = "development"
    FILE_STORAGE_PATH: str = "uploads/documents"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

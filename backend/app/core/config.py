"""SIH Problem Statement 130 - Core Configuration"""
import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    APP_NAME: str = "Bharat Compliance & Unified Approval Platform"
    APP_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Server
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000"
    ]

    # Database: Default to SQLite for seamless local dev; override with PostgreSQL in production/docker
    DATABASE_URL: str = Field(
        default="sqlite:///./app.db",
        description="Database connection string"
    )

    # JWT Authentication
    JWT_SECRET_KEY: str = "sih_super_secret_jwt_key_change_in_production_2026_hackathon"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # AI/ML Integrations
    USE_MOCK_AI_SERVICE: bool = True
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # Document Storage
    UPLOAD_DIRECTORY: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 15

settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)

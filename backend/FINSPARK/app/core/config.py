import os
from typing import Optional
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    PROJECT_NAME: str = "FinSpark Banking PAM AI Governance Platform"
    API_V1_STR: str = "/api/v1"

    # Core Security Keys
    SECRET_KEY: str = Field(
        default="SUPER_SECURE_DEV_SECRET_KEY_FOR_JWT_GENERATION_NIST_COMPLIANT_256_BITS_MINIMUM",
        description="NIST compliant secret key for HS256 JWT signature verification"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Database Configuration
    DATABASE_URL: Optional[str] = None
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "finspark_pam"
    POSTGRES_PORT: int = 5432

    @computed_field
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        if self.POSTGRES_SERVER == "localhost":
            return "sqlite+aiosqlite:///c:\\Users\\madhu\\OneDrive\\Desktop\\FINSPARK\\finspark_pam.db"
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis Configuration (Caching, Token blocklist, Rate limits)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # AI Model Engine Settings
    AI_PROVIDER_TYPE: str = "MOCK"  # Choices: MOCK, CORE_RULES, OPENAI
    AI_MODEL_VERSION: str = "fin-pam-governance-v1.4"
    AI_DECISION_CONFIDENCE_THRESHOLD: float = 0.85

    # Adaptive Authentication & Compliance Controls
    ENFORCE_IP_WHITELIST: bool = True
    ENFORCE_DEVICE_TRUST: bool = True
    MAX_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_DURATION_MINUTES: int = 30


# Global Settings instance
settings = Settings()

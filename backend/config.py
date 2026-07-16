import os

try:
    from pydantic_settings import BaseSettings
except ImportError:
    class BaseSettings:
        pass

# Standard config options
class Settings:
    PROJECT_NAME: str = "NEXUS ONE"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # LLM Settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    USE_LLM: bool = bool(os.getenv("USE_LLM", "False").lower() in ("true", "1", "yes"))
    
    # DB configuration
    DB_PATH: str = os.getenv("DB_PATH", "nexus_memory.db")
    
    # Security Configurations
    MFA_REQUIRED_CRITICALITY: str = "HIGH"

settings = Settings()

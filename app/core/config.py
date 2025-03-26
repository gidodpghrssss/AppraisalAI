from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Appraisal System"
    VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = "sqlite:///./appraisal.db"

    # Llama Stack
    LLAMA_API_KEY: str = ""
    LLAMA_API_URL: str = "http://localhost:8321"

    # External Services
    MLS_API_KEY: str = ""
    COSTAR_API_KEY: str = ""

    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

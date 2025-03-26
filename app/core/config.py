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

    # Nebius API Configuration
    NEBIUS_API_KEY: str = ""
    NEBIUS_API_URL: str = "https://api.studio.nebius.com/v1"

    # Free Data Sources
    OPENSTREETMAP_ENABLED: bool = True
    OPEN_DATA_CACHE_DIR: str = "./data/cache"
    
    # Public Property Data APIs
    ATTOM_API_KEY: str = ""  # Free tier available with limited requests
    GEOCODIO_API_KEY: str = ""  # Free tier available with limited requests
    
    # Web Search API
    BRAVE_API_KEY: str = ""  # For web search functionality

    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

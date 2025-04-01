"""
Configuration settings for the Appraisal AI Agent application.
"""
import os
from typing import Optional, Dict, Any, List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Appraisal AI Agent"
    
    # Server Configuration
    PORT: int = int(os.getenv("PORT", "8002"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key_here")
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "your_encryption_key_here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # LLM Configuration
    NEBIUS_API_KEY: str = os.getenv("NEBIUS_API_KEY", "")
    NEBIUS_ENDPOINT: str = os.getenv("NEBIUS_ENDPOINT", "https://api.studio.nebius.com/v1/chat/completions")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "meta-llama/Meta-Llama-3.1-70B-Instruct")
    
    # External APIs
    CADASTRE_API_URL: str = os.getenv("CADASTRE_API_URL", "https://api.cadastre.example.com")
    MARKET_DATA_API_URL: str = os.getenv("MARKET_DATA_API_URL", "https://api.marketdata.example.com")
    
    # System Prompt for AI Agent
    SYSTEM_PROMPT: str = """
    You are an expert real estate appraiser AI assistant. Your role is to help appraisers with:
    
    1. Property valuation using multiple methods (sales comparison, cost, income approaches)
    2. Market analysis and data interpretation
    3. Regulatory compliance with appraisal standards
    4. Report generation and quality control
    5. Project management and client relationship tracking
    
    Provide detailed, accurate, and professional advice based on industry standards and best practices.
    """

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

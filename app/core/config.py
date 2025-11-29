"""
Configuration module for Sales Analytics AI Agent
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Application Configuration
    APP_NAME: str = "Sales Analytics AI Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    # Database
    DATABASE_URL: str = "sqlite:///./sales_analytics.db"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # Agent Configuration
    MAX_ITERATIONS: int = 10
    AGENT_TEMPERATURE: float = 0.2
    AGENT_VERBOSE: bool = True
    
    # Analytics Configuration
    FORECAST_PERIODS: int = 12
    CONFIDENCE_LEVEL: float = 0.95
    
    # Data paths
    DATA_PATH: str = "data"
    MODELS_PATH: str = "models/ml_models"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Ensure necessary directories exist
os.makedirs("logs", exist_ok=True)
os.makedirs(settings.DATA_PATH, exist_ok=True)
os.makedirs(settings.MODELS_PATH, exist_ok=True)

"""
Application Configuration Management
Handles environment variables and application settings
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application Info
    APP_NAME: str = "SummarizerAI Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "https://summarizerai.vercel.app"
    ]
    
    # File Upload Configuration
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".ppt", ".pptx"]
    
    # ML Model Configuration
    ML_SERVICE_URL: Optional[str] = None  # URL to ML service if separate
    EMBEDDINGS_MODEL: str = "sentence-transformers/all-mpnet-base-v2"
    
    # FAISS Configuration
    FAISS_INDEX_DIR: str = "faiss_indices"
    
    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-3.5-turbo"
    LLM_TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 1000
    
    # Database Configuration (for future use)
    DATABASE_URL: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings
    Uses LRU cache to avoid reading .env file multiple times
    """
    return Settings()


# Create necessary directories on startup
def create_directories():
    """Create required directories if they don't exist"""
    settings = get_settings()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.FAISS_INDEX_DIR, exist_ok=True)

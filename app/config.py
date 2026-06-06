from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./invisible_work.db"
    
    # API
    API_TITLE: str = "Invisible Work Analyzer API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "API for analyzing and tracking invisible work activities"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".txt", ".csv", ".pdf", ".docx"]
    UPLOAD_DIR: str = "uploads"
    
    # Analysis
    INVISIBLE_WORK_THRESHOLD: float = 0.6
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Made with Bob

# backend/app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

class Settings(BaseSettings):
    # MongoDB
    MONGODB_URI: str
    MONGODB_DB_NAME: str = "budget_tracker"
    
    # Firebase
    FIREBASE_PROJECT_ID: str
    FIREBASE_PRIVATE_KEY: str
    FIREBASE_CLIENT_EMAIL: str
    
    # Additional Firebase fields
    FIREBASE_CLIENT_ID: Optional[str] = None
    FIREBASE_APP_ID: Optional[str] = None
    FIREBASE_STORAGE_BUCKET: Optional[str] = None
    FIREBASE_AUTH_DOMAIN: Optional[str] = None
    FIREBASE_MESSAGING_SENDER_ID: Optional[str] = None
    
    # Gemini AI
    GEMINI_API_KEY: str
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Use Pydantic v2 syntax
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False  # Make environment variable names case-insensitive
    )

settings = Settings()
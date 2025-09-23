from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"  
    MONGODB_DB_NAME: str = "budget_tracker"
    
    # Firebase
    FIREBASE_API_KEY: str = ""
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_PRIVATE_KEY: str = ""
    FIREBASE_CLIENT_EMAIL: str = ""
    FIREBASE_CLIENT_ID: str = ""
    FIREBASE_APP_ID: str = ""
    FIREBASE_STORAGE_BUCKET: str = ""
    FIREBASE_AUTH_DOMAIN: str = ""
    FIREBASE_MESSAGING_SENDER_ID: str = ""
    
    # Gemini AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
        "https://budget-tracker.jbbru.com",
        "https://budget.jbbru.com",
        "https://jbbru.com",
        "https://*.vercel.app"  # Allow Vercel preview deployments
    ]
    
    # Allow override from environment variable
    def __init__(self, **data):
        super().__init__(**data)
        cors_env = os.getenv("CORS_ORIGINS")
        if cors_env:
            try:
                import json
                # Clean up the JSON string to handle any formatting issues
                cors_env_clean = cors_env.strip().replace("'", '"')
                self.CORS_ORIGINS = json.loads(cors_env_clean)
                print(f"CORS Origins from environment: {self.CORS_ORIGINS}")
            except json.JSONDecodeError as e:
                print(f"Failed to parse CORS_ORIGINS JSON: {e}")
                # Fallback to comma-separated values
                self.CORS_ORIGINS = [origin.strip().strip('"\'') for origin in cors_env.split(",")]
                print(f"CORS Origins from CSV fallback: {self.CORS_ORIGINS}")
        else:
            print(f"Using default CORS Origins: {self.CORS_ORIGINS}")
    
    # Update to new Pydantic v2 format
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # Make environment variable names case-insensitive
        extra="ignore"  # Ignore extra fields from environment variables
    )

settings = Settings()
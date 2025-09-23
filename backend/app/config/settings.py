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
    FIREBASE_AUTH_DOMAIN: str = ""
    FIREBASE_MESSAGING_SENDER_ID: str = ""
    FIREBASE_SERVICE_ACCOUNT_PATH: str = "firebase-service-account.json"
    
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
        
        # Always ensure the frontend domain is included
        required_origins = [
            "https://budget-tracker.jbbru.com",
            "https://budget.jbbru.com", 
            "http://localhost:3000"
        ]
        
        cors_env = os.getenv("CORS_ORIGINS")
        if cors_env:
            try:
                # First try JSON parsing
                import json
                cors_env_clean = cors_env.strip().replace("'", '"')
                env_origins = json.loads(cors_env_clean)
                print(f"CORS Origins from JSON: {env_origins}")
            except json.JSONDecodeError:
                # Fallback to comma-separated values
                env_origins = [origin.strip().strip('"\'') for origin in cors_env.split(",")]
                print(f"CORS Origins from CSV: {env_origins}")
            
            # Combine environment origins with required origins
            all_origins = list(set(env_origins + required_origins + self.CORS_ORIGINS))
            self.CORS_ORIGINS = all_origins
            print(f"Final CORS Origins: {self.CORS_ORIGINS}")
        else:
            # No environment variable, add required origins to defaults
            self.CORS_ORIGINS = list(set(required_origins + self.CORS_ORIGINS))
            print(f"Using default + required CORS Origins: {self.CORS_ORIGINS}")
    
    # Update to new Pydantic v2 format
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # Make environment variable names case-insensitive
        extra="ignore"  # Ignore extra fields from environment variables
    )

settings = Settings()
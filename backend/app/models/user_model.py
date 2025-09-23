# app/models/user_model.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    display_name: Optional[str] = None

class UserResponse(BaseModel):
    uid: str
    email: EmailStr
    display_name: Optional[str] = None
    message: Optional[str] = None

class UserProfile(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    firebase_uid: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    avatar: Optional[str] = None
    monthly_budget: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    preferences: Optional[Dict] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    avatar: Optional[str] = None
    monthly_budget: Optional[float] = None
    preferences: Optional[Dict] = None
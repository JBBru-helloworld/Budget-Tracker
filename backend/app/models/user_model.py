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
    user_id: str
    email: EmailStr
    display_name: Optional[str] = None
    avatar: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    preferences: Optional[Dict] = None

class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    avatar: Optional[str] = None
    preferences: Optional[Dict] = None
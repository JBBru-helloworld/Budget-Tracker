# app/models/category_model.py
from pydantic import BaseModel, Field
from typing import Optional, List
from bson import ObjectId

class Category(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    color: Optional[str] = "#6b7280"  # Default gray color
    icon: Optional[str] = None
    is_system: bool = False
    user_id: Optional[str] = None  # None for system categories
    
    class Config:
        json_encoders = {
            ObjectId: lambda v: str(v)
        }

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = "#6b7280"
    icon: Optional[str] = None
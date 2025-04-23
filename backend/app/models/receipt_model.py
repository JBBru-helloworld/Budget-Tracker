# app/models/receipt_model.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from bson import ObjectId

class ReceiptItem(BaseModel):
    name: str
    price: float
    quantity: Optional[float] = 1.0
    category: Optional[str] = "Uncategorized"
    shared_with: Optional[List[str]] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            ObjectId: lambda v: str(v)
        }

class ReceiptCreate(BaseModel):
    store_name: str
    date: datetime
    items: List[ReceiptItem]
    total_amount: float
    image_path: Optional[str] = None
    shared_with: Optional[List[str]] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            ObjectId: lambda v: str(v)
        }

class ReceiptResponse(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    store_name: Optional[str] = None
    date: Optional[datetime] = None
    items: Optional[List[ReceiptItem]] = None
    total_amount: Optional[float] = None
    image_path: Optional[str] = None
    shared_with: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    message: Optional[str] = None
    
    class Config:
        json_encoders = {
            ObjectId: lambda v: str(v)
        }
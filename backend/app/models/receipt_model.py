# app/models/receipt_model.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from datetime import datetime
from bson import ObjectId

class SharedExpense(BaseModel):
    user_id: str
    amount: float
    items: List[str]  # List of item IDs assigned to this user

class ReceiptItem(BaseModel):
    id: Optional[str] = None
    name: str
    price: float
    quantity: Optional[float] = 1.0
    category: str
    assigned_to: Optional[str] = None  # User ID of the person this item is assigned to
    shared_with: List[SharedExpense] = []  # List of users sharing this item

class Receipt(BaseModel):
    id: Optional[str] = None
    user_id: str
    date: datetime
    total_amount: float
    store_name: Optional[str] = None
    items: List[ReceiptItem]
    image_url: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_shared: bool = False
    shared_expenses: List[SharedExpense] = []

    class Config:
        json_encoders = {
            ObjectId: lambda v: str(v),
            datetime: lambda v: v.isoformat()
        }

class ReceiptCreate(BaseModel):
    date: datetime
    total_amount: float
    store_name: Optional[str] = None
    items: List[ReceiptItem]
    image_url: str
    is_shared: bool = False
    shared_expenses: List[SharedExpense] = []

class ReceiptUpdate(BaseModel):
    date: Optional[datetime] = None
    total_amount: Optional[float] = None
    store_name: Optional[str] = None
    items: Optional[List[ReceiptItem]] = None
    is_shared: Optional[bool] = None
    shared_expenses: Optional[List[SharedExpense]] = None

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

class ProcessedReceiptResponse(BaseModel):
    extracted_text: str
    processed_data: Dict
    image_path: Optional[str] = None
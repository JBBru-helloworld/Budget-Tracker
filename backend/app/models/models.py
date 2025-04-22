# backend/app/models/models.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from enum import Enum

# Custom ObjectId field to handle MongoDB's ObjectId
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# Base model for MongoDB documents
class MongoBaseModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        json_encoders = {
            ObjectId: str
        }
        populate_by_name = True

# Category Enum
class Category(str, Enum):
    FOOD = "food"
    CLOTHING = "clothing"
    RECREATION = "recreation"
    TRANSPORTATION = "transportation"
    HOUSING = "housing"
    UTILITIES = "utilities"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    PERSONAL = "personal"
    OTHER = "other"

# Receipt Item model
class ReceiptItem(BaseModel):
    name: str
    price: float
    quantity: int = 1
    category: Category = Category.OTHER
    assigned_to: Optional[str] = None  # User ID of person assigned to pay
    assigned_percentage: Optional[float] = None  # Percentage of cost assigned (if split)

# Receipt model
class Receipt(MongoBaseModel):
    user_id: str
    date: datetime
    store_name: str
    total_amount: float
    items: List[ReceiptItem]
    image_url: Optional[str] = None
    raw_text: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('updated_at', always=True)
    def set_updated_at(cls, v, values):
        return datetime.utcnow()

# User Profile model
class UserProfile(MongoBaseModel):
    user_id: str  # Firebase Auth user ID
    email: str
    display_name: Optional[str] = None
    budget_targets: Dict[Category, float] = {}  # Monthly budget targets by category
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Expense Summary model (for analytics)
class ExpenseSummary(BaseModel):
    period: str  # 'week', 'month', 'year'
    start_date: datetime
    end_date: datetime
    total_amount: float
    by_category: Dict[Category, float]
    
# Money-saving Tip model
class SavingTip(MongoBaseModel):
    category: Category
    title: str
    description: str
    ai_generated: bool = True
    relevance_score: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
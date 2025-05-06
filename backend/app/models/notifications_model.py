from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime

class Notification(BaseModel):
    id: Optional[str] = None
    user_id: str
    type: Literal["receipt", "budget", "tip", "alert", "system"]
    title: str
    message: str
    link: Optional[str] = None
    image_url: Optional[str] = None
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "id": "notification123",
                "user_id": "user123",
                "type": "receipt",
                "title": "New Receipt Added",
                "message": "Your Walmart receipt for $45.67 was added successfully",
                "link": "/receipts/receipt123",
                "image_url": "https://example.com/receipt_icon.png",
                "is_read": False,
                "created_at": "2025-05-06T10:30:00"
            }
        }

class NotificationCreate(BaseModel):
    user_id: str
    type: Literal["receipt", "budget", "tip", "alert", "system"]
    title: str
    message: str
    link: Optional[str] = None
    image_url: Optional[str] = None

class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None

class NotificationResponse(BaseModel):
    id: str
    type: str
    title: str
    message: str
    link: Optional[str] = None
    image_url: Optional[str] = None
    is_read: bool
    created_at: datetime
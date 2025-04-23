# app/models/settings_model.py
from pydantic import BaseModel
from typing import Optional, Dict

class NotificationSettings(BaseModel):
    email: bool = True
    push: bool = False
    budget_alerts: bool = True

class UserSettings(BaseModel):
    user_id: str
    theme: str = "light"
    currency: str = "USD"
    budget_limits: Dict[str, float] = {}  # category: amount
    notifications: NotificationSettings
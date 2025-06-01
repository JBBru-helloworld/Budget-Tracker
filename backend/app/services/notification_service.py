from typing import Dict, Any, Optional, List
import os
import google.generativeai as genai
from datetime import datetime
from bson import ObjectId
from app.config.mongodb import get_database

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Database Operations
async def create_notification_in_db(notification_data: Dict[str, Any]) -> str:
    # Create a new notification in the database
    db = get_database()
    notification_data["created_at"] = datetime.now()
    result = await db.notifications.insert_one(notification_data)
    return str(result.inserted_id)

async def get_notifications_from_db(user_id: str, limit: int = 50, skip: int = 0, include_read: bool = False) -> List[Dict[str, Any]]:
    # Get user's notifications from database
    db = get_database()
    query = {"user_id": user_id}
    if not include_read:
        query["is_read"] = False
    
    cursor = db.notifications.find(query).sort("created_at", -1).skip(skip).limit(limit)
    
    notifications = []
    async for notification in cursor:
        notification["id"] = str(notification.pop("_id"))
        notifications.append(notification)
    
    return notifications

async def mark_notification_read_in_db(notification_id: str, user_id: str) -> bool:
    # Mark a notification as read in the database
    db = get_database()
    result = await db.notifications.update_one(
        {"_id": ObjectId(notification_id), "user_id": user_id},
        {"$set": {"is_read": True}}
    )
    return result.modified_count > 0

async def mark_all_read_in_db(user_id: str) -> int:
    # Mark all notifications as read in the database
    db = get_database()
    result = await db.notifications.update_many(
        {"user_id": user_id, "is_read": False},
        {"$set": {"is_read": True}}
    )
    return result.modified_count

async def get_unread_count_from_db(user_id: str) -> int:
    # Get count of unread notifications from database
    db = get_database()
    return await db.notifications.count_documents({"user_id": user_id, "is_read": False})

# Service Operations
async def create_receipt_notification(user_id: str, receipt_data: Dict[str, Any]) -> str:
    # Create notification when a receipt is added
    store = receipt_data.get("store_name", "Unknown store")
    total = receipt_data.get("total_amount", 0)
    receipt_id = receipt_data.get("id", "")
    
    notification = {
        "user_id": user_id,
        "type": "receipt",
        "title": f"Receipt Added: {store}",
        "message": f"Your receipt from {store} for ${total:.2f} was added successfully.",
        "link": f"/receipts/{receipt_id}",
        "image_url": "/icons/receipt.png",
        "is_read": False
    }
    
    return await create_notification_in_db(notification)

# Add the other service functions as well...

# Public API
async def get_user_notifications(user_id: str, limit: int = 20, include_read: bool = False):
    # Get a user's notifications
    return await get_notifications_from_db(user_id, limit, include_read=include_read)

async def mark_as_read(notification_id: str, user_id: str):
    # Mark notification as read
    return await mark_notification_read_in_db(notification_id, user_id)

async def mark_all_notifications_read(user_id: str):
    # Mark all notifications as read
    return await mark_all_read_in_db(user_id)

async def get_notification_count(user_id: str):
    # Get count of unread notifications
    return await get_unread_count_from_db(user_id)

async def create_budget_notification(user_id: str, category: str, current: float, limit: float) -> str:
    # Create notification when budget limit is approached/exceeded
    percentage = (current / limit) * 100
    
    if percentage >= 90:
        status = "exceeded" if percentage > 100 else "approaching"
        title = f"Budget Alert: {category}"
        message = f"You've {status} your budget for {category}. Current: ${current:.2f}, Limit: ${limit:.2f}"
        
        notification = {
            "user_id": user_id,
            "type": "budget",
            "title": title,
            "message": message,
            "link": "/dashboard",
            "image_url": "/icons/alert.png",
            "is_read": False
        }
        
        return await create_notification_in_db(notification)
    
    return None

async def generate_budget_tip(user_id: str, expenses: List[Dict[str, Any]]) -> Optional[str]:
    # Generate a personalized budget tip using Gemini
    if not expenses:
        return None
        
    try:
        # Format expenses data for Gemini
        expense_summary = "\n".join([
            f"- {expense.get('category', 'Misc')}: ${expense.get('amount', 0):.2f}"
            for expense in expenses[:10]  # Limit to 10 expenses for prompt size
        ])
        
        prompt = f"""
        Based on these recent expenses:
        
        {expense_summary}
        
        Provide one concise, specific, and actionable budgeting tip (no more than 2 sentences) 
        to help save money or manage finances better.
        
        Format your response as a single tip without any prefixes or explanations.
        """
        
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        tip = response.text.strip()
        
        notification = {
            "user_id": user_id,
            "type": "tip",
            "title": "Budget Tip",
            "message": tip,
            "is_read": False
        }
        
        return await create_notification_in_db(notification)
        
    except Exception as e:
        print(f"Error generating budget tip: {str(e)}")
        return None
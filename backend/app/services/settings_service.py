# app/services/settings_service.py
from datetime import datetime
from app.config.mongodb import get_database

async def get_user_settings(user_id):
    # Get user settings.
    db = get_database()
    settings = await db.user_settings.find_one({"user_id": user_id})
    
    if settings:
        settings["_id"] = str(settings["_id"])
        return settings
    
    return None

async def update_user_settings(user_id, settings_data):
    # Update user settings.
    db = get_database()
    settings_data["updated_at"] = datetime.now()
    
    # Check if settings exist
    existing_settings = await db.user_settings.find_one({"user_id": user_id})
    
    if existing_settings:
        # Update existing settings
        result = await db.user_settings.update_one(
            {"user_id": user_id},
            {"$set": settings_data}
        )
        
        if result.modified_count:
            # Get and return updated settings
            updated_settings = await db.user_settings.find_one({"user_id": user_id})
            updated_settings["_id"] = str(updated_settings["_id"])
            return updated_settings
    else:
        # Create new settings
        settings_data["user_id"] = user_id
        settings_data["created_at"] = datetime.now()
        
        result = await db.user_settings.insert_one(settings_data)
        
        # Get and return created settings
        created_settings = await db.user_settings.find_one({"_id": result.inserted_id})
        created_settings["_id"] = str(created_settings["_id"])
        return created_settings
    
    return None
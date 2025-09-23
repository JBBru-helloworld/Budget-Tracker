# app/services/user_service.py
from datetime import datetime
from app.config.mongodb import get_database
from bson import ObjectId
from firebase_admin import auth
from firebase_admin.exceptions import FirebaseError

async def create_user_profile(user_data):
    # Create a new user profile in MongoDB.
    db = get_database()
    user_data["created_at"] = datetime.now()
    user_data["updated_at"] = datetime.now()
    
    # Ensure email is included if not provided
    if "email" not in user_data and "firebase_uid" in user_data:
        try:
            firebase_user = auth.get_user(user_data["firebase_uid"])
            user_data["email"] = firebase_user.email or "user@example.com"
        except FirebaseError:
            user_data["email"] = "user@example.com"
    
    # Insert user profile
    result = await db.user_profiles.insert_one(user_data)
    
    # Get and return created profile
    user_profile = await db.user_profiles.find_one({"_id": result.inserted_id})
    user_profile["_id"] = str(user_profile["_id"])
    return user_profile

async def get_user_profile(firebase_uid):
    # Get user profile by Firebase UID.
    db = get_database()
    user_profile = await db.user_profiles.find_one({"firebase_uid": firebase_uid})
    
    if user_profile:
        user_profile["_id"] = str(user_profile["_id"])
        
        # Ensure email field exists (required by UserProfile model)
        if "email" not in user_profile:
            try:
                # Get email from Firebase user record
                firebase_user = auth.get_user(firebase_uid)
                user_profile["email"] = firebase_user.email or "user@example.com"
            except FirebaseError:
                # Fallback email if Firebase lookup fails
                user_profile["email"] = "user@example.com"
        
        return user_profile
    
    return None

async def update_user_profile(firebase_uid, update_data):
    # Update user profile.
    db = get_database()
    update_data["updated_at"] = datetime.now()
    
    # Update profile
    result = await db.user_profiles.update_one(
        {"firebase_uid": firebase_uid},
        {"$set": update_data}
    )
    
    # Check if the document was matched (exists), not just modified
    if result.matched_count:
        # Get and return updated profile
        user_profile = await db.user_profiles.find_one({"firebase_uid": firebase_uid})
        user_profile["_id"] = str(user_profile["_id"])
        
        # Ensure email field exists (required by UserProfile model)
        if "email" not in user_profile:
            try:
                firebase_user = auth.get_user(firebase_uid)
                user_profile["email"] = firebase_user.email or "user@example.com"
            except FirebaseError:
                user_profile["email"] = "user@example.com"
        
        return user_profile
    
    return None
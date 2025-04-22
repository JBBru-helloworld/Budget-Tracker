import os
from datetime import datetime
from bson import ObjectId
from typing import List, Optional
import firebase_admin
from firebase_admin import storage
from ..utils.db import get_database

class UserProfileService:
    def __init__(self):
        self.db = get_database()
        self.profiles_collection = self.db.user_profiles
    
    async def create_profile(self, profile_data):
        profile_dict = profile_data.dict(by_alias=True)
        result = await self.profiles_collection.insert_one(profile_dict)
        profile_dict["_id"] = str(result.inserted_id)
        return profile_dict
    
    async def get_profile_by_user_id(self, user_id):
        profile = await self.profiles_collection.find_one({"user_id": user_id})
        if profile:
            profile["_id"] = str(profile["_id"])
        return profile
    
    async def update_profile(self, user_id, profile_update):
        # Make sure _id is not in the update
        if "_id" in profile_update:
            del profile_update["_id"]
        
        profile_update["updated_at"] = datetime.now()
        
        result = await self.profiles_collection.update_one(
            {"user_id": user_id},
            {"$set": profile_update}
        )
        
        if result.modified_count == 0:
            return None
        
        updated_profile = await self.get_profile_by_user_id(user_id)
        return updated_profile
    
    async def upload_avatar(self, user_id, file):
        # Get file contents
        contents = await file.read()
        
        # Upload to Firebase Storage
        bucket = storage.bucket()
        blob = bucket.blob(f"avatars/{user_id}/{file.filename}")
        blob.upload_from_string(contents, content_type=file.content_type)
        
        # Make the blob publicly accessible
        blob.make_public()
        avatar_url = blob.public_url
        
        # Update profile with new avatar URL
        await self.update_profile(user_id, {"avatar_url": avatar_url})
        
        return avatar_url
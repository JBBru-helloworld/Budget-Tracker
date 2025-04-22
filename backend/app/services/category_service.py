from datetime import datetime
from bson import ObjectId
from typing import List, Optional
from ..utils.db import get_database

class CategoryService:
    def __init__(self):
        self.db = get_database()
        self.categories_collection = self.db.categories
    
    async def create_category(self, category_data):
        category_dict = category_data.dict(by_alias=True)
        result = await self.categories_collection.insert_one(category_dict)
        category_dict["_id"] = str(result.inserted_id)
        return category_dict
    
    async def get_categories_by_user_id(self, user_id):
        cursor = self.categories_collection.find({"user_id": user_id})
        categories = []
        async for category in cursor:
            category["_id"] = str(category["_id"])
            categories.append(category)
        return categories
    
    async def get_category_by_id(self, category_id):
        try:
            category = await self.categories_collection.find_one({"_id": ObjectId(category_id)})
            if category:
                category["_id"] = str(category["_id"])
            return category
        except:
            return None
    
    async def update_category(self, category_id, category_update):
        # Make sure _id is not in the update
        if "_id" in category_update:
            del category_update["_id"]
        
        category_update["updated_at"] = datetime.now()
        
        await self.categories_collection.update_one(
            {"_id": ObjectId(category_id)},
            {"$set": category_update}
        )
        
        updated_category = await self.get_category_by_id(category_id)
        return updated_category
    
    async def delete_category(self, category_id):
        result = await self.categories_collection.delete_one({"_id": ObjectId(category_id)})
        return result.deleted_count > 0
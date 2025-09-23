from datetime import datetime
from bson import ObjectId
from typing import List, Optional
from app.config.mongodb import get_database

class CategoryService:
    def __init__(self):
        self.db = None
        self.categories_collection = None
    
    async def initialize(self):
        if self.db is None:
            self.db = get_database()
            self.categories_collection = self.db.categories
    
    async def create_category(self, category_data):
        await self.initialize()
        # category_data is already a dictionary
        category_dict = category_data.copy()
        category_dict["created_at"] = datetime.now()
        category_dict["updated_at"] = datetime.now()
        result = await self.categories_collection.insert_one(category_dict)
        category_dict["_id"] = str(result.inserted_id)
        return category_dict
    
    async def get_categories_by_user_id(self, user_id):
        await self.initialize()
        cursor = self.categories_collection.find({"user_id": user_id})
        categories = []
        async for category in cursor:
            category["_id"] = str(category["_id"])
            categories.append(category)
        return categories
    
    async def get_category_by_id(self, category_id):
        await self.initialize()
        try:
            category = await self.categories_collection.find_one({"_id": ObjectId(category_id)})
            if category:
                category["_id"] = str(category["_id"])
            return category
        except:
            return None
    
    async def update_category(self, category_id, category_update):
        await self.initialize()
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
        await self.initialize()
        result = await self.categories_collection.delete_one({"_id": ObjectId(category_id)})
        return result.deleted_count > 0

# Create a singleton instance
category_service = CategoryService()

# Expose standalone functions that use the singleton instance
async def get_all_categories(user_id: str, include_system: bool = True):
    categories = await category_service.get_categories_by_user_id(user_id)
    
    # Add default system categories if include_system is True
    if include_system:
        default_categories = [
            {"_id": "system_food", "name": "Food & Dining", "icon": "🍽️", "color": "#FF6B6B", "user_id": None},
            {"_id": "system_transport", "name": "Transportation", "icon": "🚗", "color": "#4ECDC4", "user_id": None},
            {"_id": "system_shopping", "name": "Shopping", "icon": "🛍️", "color": "#45B7D1", "user_id": None},
            {"_id": "system_bills", "name": "Bills & Utilities", "icon": "💡", "color": "#FFA726", "user_id": None},
            {"_id": "system_healthcare", "name": "Healthcare", "icon": "🏥", "color": "#EF5350", "user_id": None},
            {"_id": "system_entertainment", "name": "Entertainment", "icon": "🎬", "color": "#AB47BC", "user_id": None},
            {"_id": "system_education", "name": "Education", "icon": "📚", "color": "#66BB6A", "user_id": None},
            {"_id": "system_misc", "name": "Miscellaneous", "icon": "📦", "color": "#8D6E63", "user_id": None}
        ]
        
        # Add default categories that user doesn't have custom versions of
        user_category_names = {cat.get("name", "").lower() for cat in categories}
        for default_cat in default_categories:
            if default_cat["name"].lower() not in user_category_names:
                categories.append(default_cat)
    
    return categories

async def create_category(user_id: str, category_data: dict):
    category_data["user_id"] = user_id
    return await category_service.create_category(category_data)

async def update_category(category_id: str, user_id: str, category_data: dict):
    # Verify the category belongs to the user
    category = await category_service.get_category_by_id(category_id)
    if not category or category.get("user_id") != user_id:
        return None
    return await category_service.update_category(category_id, category_data)

async def delete_category(category_id: str, user_id: str):
    # Verify the category belongs to the user
    category = await category_service.get_category_by_id(category_id)
    if not category or category.get("user_id") != user_id:
        return False
    return await category_service.delete_category(category_id)
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.category_model import Category, CategoryCreate
from app.config.mongodb import get_database
from app.middleware.auth_middleware import get_current_user
from bson import ObjectId

router = APIRouter()

@router.get("/categories", response_model=List[Category])
async def get_categories(current_user: dict = Depends(get_current_user)):
    db = await get_database()
    categories = await db.categories.find({"user_id": current_user["uid"]}).to_list(length=None)
    return [Category(**category, id=str(category["_id"])) for category in categories]

@router.post("/categories", response_model=Category, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, current_user: dict = Depends(get_current_user)):
    db = await get_database()
    category_data = category.dict()
    category_data["user_id"] = current_user["uid"]
    
    result = await db.categories.insert_one(category_data)
    created_category = await db.categories.find_one({"_id": result.inserted_id})
    return Category(**created_category, id=str(created_category["_id"]))

@router.put("/categories/{category_id}", response_model=Category)
async def update_category(
    category_id: str,
    category: CategoryCreate,
    current_user: dict = Depends(get_current_user)
):
    db = await get_database()
    
    # Check if category exists and belongs to user
    existing_category = await db.categories.find_one({
        "_id": ObjectId(category_id),
        "user_id": current_user["uid"]
    })
    
    if not existing_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Update category
    category_data = category.dict()
    await db.categories.update_one(
        {"_id": ObjectId(category_id)},
        {"$set": category_data}
    )
    
    # Return updated category
    updated_category = await db.categories.find_one({"_id": ObjectId(category_id)})
    return Category(**updated_category, id=str(updated_category["_id"]))

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: str, current_user: dict = Depends(get_current_user)):
    db = await get_database()
    
    # Check if category exists and belongs to user
    existing_category = await db.categories.find_one({
        "_id": ObjectId(category_id),
        "user_id": current_user["uid"]
    })
    
    if not existing_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Delete category
    await db.categories.delete_one({"_id": ObjectId(category_id)})
    return None 
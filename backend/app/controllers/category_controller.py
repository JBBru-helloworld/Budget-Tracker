from fastapi import APIRouter, Body, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import List

from ..models.category import CategoryModel
from ..services.category_service import CategoryService
from ..middleware.auth_middleware import get_current_user

router = APIRouter()
category_service = CategoryService()

@router.post("/", response_description="Create category")
async def create_category(
    category: CategoryModel = Body(...),
    current_user: dict = Depends(get_current_user)
):
    if category.user_id != current_user["uid"]:
        raise HTTPException(status_code=403, detail="User ID mismatch")
    
    result = await category_service.create_category(category)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

@router.get("/", response_description="List all categories")
async def list_categories(
    current_user: dict = Depends(get_current_user)
):
    categories = await category_service.get_categories_by_user_id(current_user["uid"])
    return categories

@router.get("/{category_id}", response_description="Get category")
async def get_category(
    category_id: str,
    current_user: dict = Depends(get_current_user)
):
    category = await category_service.get_category_by_id(category_id)
    
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    if category["user_id"] != current_user["uid"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return category

@router.put("/{category_id}", response_description="Update category")
async def update_category(
    category_id: str,
    category_update: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    category = await category_service.get_category_by_id(category_id)
    
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    if category["user_id"] != current_user["uid"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    updated_category = await category_service.update_category(category_id, category_update)
    return updated_category

@router.delete("/{category_id}", response_description="Delete category")
async def delete_category(
    category_id: str,
    current_user: dict = Depends(get_current_user)
):
    category = await category_service.get_category_by_id(category_id)
    
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    if category["user_id"] != current_user["uid"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    delete_result = await category_service.delete_category(category_id)
    
    if delete_result:
        return {"message": "Category deleted successfully"}
    
    raise HTTPException(status_code=400, detail="Failed to delete category")

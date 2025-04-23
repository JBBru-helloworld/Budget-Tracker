# app/controllers/category_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.models.category_model import Category, CategoryCreate
from app.services.category_service import get_all_categories, create_category, update_category, delete_category
from app.controllers.auth_controller import verify_token

router = APIRouter()

@router.get("/", response_model=List[Category])
async def get_categories(
    user_id: str = Depends(verify_token),
    system_categories: bool = True
):
    """
    Get all categories (system default + user custom)
    """
    try:
        categories = await get_all_categories(user_id["uid"], include_system=system_categories)
        return categories
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching categories: {str(e)}"
        )

@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
async def add_category(
    category: CategoryCreate,
    user_id: str = Depends(verify_token)
):
    """
    Create a custom category
    """
    try:
        new_category = await create_category(user_id["uid"], category.dict())
        return new_category
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating category: {str(e)}"
        )

@router.put("/{category_id}", response_model=Category)
async def modify_category(
    category_id: str,
    category_data: dict,
    user_id: str = Depends(verify_token)
):
    """
    Update a custom category
    """
    try:
        updated_category = await update_category(category_id, user_id["uid"], category_data)
        if not updated_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found or you don't have permission to modify it"
            )
        
        return updated_category
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating category: {str(e)}"
        )

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_category(
    category_id: str,
    user_id: str = Depends(verify_token)
):
    """
    Delete a custom category
    """
    try:
        result = await delete_category(category_id, user_id["uid"])
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found or you don't have permission to delete it"
            )
        
        return {"message": "Category deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting category: {str(e)}"
        )
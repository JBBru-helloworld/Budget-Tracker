# app/controllers/profile_controller.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import Optional
import os
from app.models.user_model import UserProfile, UserProfileUpdate
from app.services.user_service import get_user_profile, update_user_profile
from app.controllers.auth_controller import verify_token

router = APIRouter()

@router.get("/", response_model=UserProfile)
async def get_profile(user_id: str = Depends(verify_token)):

    # Get user profile information
    try:
        profile = await get_user_profile(user_id["uid"])
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user profile: {str(e)}"
        )

@router.put("/", response_model=UserProfile)
async def update_profile(
    profile_update: UserProfileUpdate,
    user_id: str = Depends(verify_token)
):

    # Update user profile information
    try:
        updated_profile = await update_user_profile(user_id["uid"], profile_update.dict(exclude_unset=True))
        if not updated_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return updated_profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user profile: {str(e)}"
        )

@router.post("/avatar", response_model=UserProfile)
async def upload_avatar(
    file: UploadFile = File(...),
    user_id: str = Depends(verify_token)
):
    """
    Upload user avatar image
    """
    # Validate image format
    allowed_extensions = ["jpg", "jpeg", "png"]
    file_ext = file.filename.split(".")[-1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Avatar must be one of {', '.join(allowed_extensions)}"
        )
    
    try:
        # Create avatars directory if it doesn't exist
        os.makedirs("static/avatars", exist_ok=True)
        
        # Save avatar image
        avatar_path = f"static/avatars/{user_id['uid']}.{file_ext}"
        with open(avatar_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # Update user profile with avatar path
        updated_profile = await update_user_profile(user_id["uid"], {"avatar": avatar_path})
        if not updated_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return updated_profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading avatar: {str(e)}"
        )
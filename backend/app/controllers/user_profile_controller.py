# app/controllers/profile_controller.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import Optional
import os
from app.models.user_model import UserProfile, UserProfileUpdate
from app.services.user_service import get_user_profile, update_user_profile, create_user_profile
from app.services.firebase_service import get_user_id_from_token
from app.services.storage_service import storage_service

router = APIRouter()

@router.get("/", response_model=UserProfile)
async def get_profile(user_id: str = Depends(get_user_id_from_token)):

    # Get user profile information
    try:
        print(f"DEBUG: get_profile called for user: {user_id}")
        profile = await get_user_profile(user_id)
        print(f"DEBUG: Retrieved profile: {profile}")
        if not profile:
            print(f"DEBUG: No profile found for user: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return profile
    except HTTPException:
        # Re-raise HTTP exceptions (like 404) without modification
        raise
    except Exception as e:
        print(f"DEBUG: Error in get_profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user profile: {str(e)}"
        )

@router.post("/", response_model=UserProfile)
async def create_profile(
    profile_data: UserProfileUpdate,
    user_id: str = Depends(get_user_id_from_token)
):
    # Create a new user profile
    try:
        # Check if profile already exists
        existing_profile = await get_user_profile(user_id)
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User profile already exists"
            )
        
        # Prepare profile data
        profile_dict = profile_data.dict(exclude_unset=True)
        profile_dict["firebase_uid"] = user_id
        
        # Create the profile
        created_profile = await create_user_profile(profile_dict)
        
        return created_profile
        
    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user profile: {str(e)}"
        )

@router.put("/", response_model=UserProfile)
async def update_profile(
    profile_update: UserProfileUpdate,
    user_id: str = Depends(get_user_id_from_token)
):

    # Update user profile information
    try:
        # Check if profile exists
        existing_profile = await get_user_profile(user_id)
        
        if not existing_profile:
            # Profile doesn't exist, create it
            profile_dict = profile_update.dict(exclude_unset=True)
            profile_dict["firebase_uid"] = user_id
            
            created_profile = await create_user_profile(profile_dict)
            return created_profile
        else:
            # Profile exists, update it
            updated_profile = await update_user_profile(user_id, profile_update.dict(exclude_unset=True))
            if not updated_profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )
            
            return updated_profile
            
    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user profile: {str(e)}"
        )

@router.post("/avatar", response_model=UserProfile)
async def upload_avatar(
    file: UploadFile = File(...),
    user_id: str = Depends(get_user_id_from_token)
):
    """Upload user avatar image to Firebase Storage"""
    
    try:
        # Upload to Firebase Storage and get public URL
        avatar_url = await storage_service.upload_avatar(file, user_id)
        
        # Update user profile with avatar URL
        updated_profile = await update_user_profile(user_id, {"avatar": avatar_url})
        if not updated_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return updated_profile
    except HTTPException:
        # Re-raise HTTP exceptions from storage service
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading avatar: {str(e)}"
        )
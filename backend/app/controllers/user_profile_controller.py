from fastapi import APIRouter, Body, HTTPException, Depends, status, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List

from ..models.user_profile import UserProfileModel
from ..services.user_profile_service import UserProfileService
from ..middleware.auth_middleware import get_current_user

router = APIRouter()
user_profile_service = UserProfileService()

@router.post("/", response_description="Create user profile")
async def create_user_profile(
    profile: UserProfileModel = Body(...),
    current_user: dict = Depends(get_current_user)
):
    if profile.user_id != current_user["uid"]:
        raise HTTPException(status_code=403, detail="User ID mismatch")
    
    result = await user_profile_service.create_profile(profile)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

@router.get("/{user_id}", response_description="Get user profile")
async def get_user_profile(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    if user_id != current_user["uid"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    profile = await user_profile_service.get_profile_by_user_id(user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile

@router.put("/{user_id}", response_description="Update user profile")
async def update_user_profile(
    user_id: str,
    profile_update: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    if user_id != current_user["uid"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    updated_profile = await user_profile_service.update_profile(user_id, profile_update)
    if updated_profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return updated_profile

@router.post("/{user_id}/avatar", response_description="Upload avatar")
async def upload_avatar(
    user_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    if user_id != current_user["uid"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check file type
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Only JPEG, JPG or PNG files allowed")
    
    avatar_url = await user_profile_service.upload_avatar(user_id, file)
    return {"avatar_url": avatar_url}
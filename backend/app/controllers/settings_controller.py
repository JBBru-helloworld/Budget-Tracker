# app/controllers/settings_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from app.models.settings_model import UserSettings, NotificationSettings
from app.services.settings_service import get_user_settings, update_user_settings
from app.controllers.auth_controller import verify_token

router = APIRouter()

@router.get("/", response_model=UserSettings)
async def get_settings(user_id: str = Depends(verify_token)):
    """
    Get user settings
    """
    try:
        settings = await get_user_settings(user_id["uid"])
        if not settings:
            # Initialize default settings if not found
            settings = {
                "user_id": user_id["uid"],
                "theme": "light",
                "currency": "USD",
                "budget_limits": {},
                "notifications": {
                    "email": True,
                    "push": False,
                    "budget_alerts": True
                }
            }
            await update_user_settings(user_id["uid"], settings)
        
        return settings
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching settings: {str(e)}"
        )

@router.put("/", response_model=UserSettings)
async def update_settings(
    settings_update: dict,
    user_id: str = Depends(verify_token)
):
    """
    Update user settings
    """
    try:
        updated_settings = await update_user_settings(user_id["uid"], settings_update)
        if not updated_settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Settings not found"
            )
        
        return updated_settings
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating settings: {str(e)}"
        )

@router.put("/notifications", response_model=NotificationSettings)
async def update_notification_settings(
    notification_settings: NotificationSettings,
    user_id: str = Depends(verify_token)
):
    """
    Update notification settings
    """
    try:
        current_settings = await get_user_settings(user_id["uid"])
        if not current_settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User settings not found"
            )
        
        # Update only notification settings
        current_settings["notifications"] = notification_settings.dict()
        updated_settings = await update_user_settings(user_id["uid"], current_settings)
        
        return updated_settings["notifications"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating notification settings: {str(e)}"
        )
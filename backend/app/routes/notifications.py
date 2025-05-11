from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import List
from ..services.notification_service import (
    get_user_notifications, 
    mark_as_read, 
    mark_all_notifications_read,
    get_notification_count
)
from ..models.notifications_model import NotificationResponse
from ..services.firebase_service import verify_firebase_token

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    include_read: bool = False,
    limit: int = Query(20, gt=0, le=100),
    firebase_uid: str = Depends(verify_firebase_token)
):
    """Get user's notifications"""
    try:
        notifications = await get_user_notifications(
            user_id=firebase_uid,
            limit=limit,
            include_read=include_read
        )
        
        return notifications
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve notifications: {str(e)}"
        )

@router.get("/count", response_model=int)
async def get_unread_notification_count(
    firebase_uid: str = Depends(verify_firebase_token)
):
    """Get count of unread notifications"""
    try:
        count = await get_notification_count(firebase_uid)
        return count
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get notification count: {str(e)}"
        )

@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str = Path(..., title="Notification ID"),
    firebase_uid: str = Depends(verify_firebase_token)
):
    """Mark a notification as read"""
    try:
        success = await mark_as_read(notification_id, firebase_uid)
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Notification not found"
            )
        
        return {"message": "Notification marked as read"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to mark notification as read: {str(e)}"
        )

@router.put("/read-all")
async def mark_all_read(
    firebase_uid: str = Depends(verify_firebase_token)
):
    """Mark all notifications as read"""
    try:
        count = await mark_all_notifications_read(firebase_uid)
        return {"message": f"Marked {count} notifications as read"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to mark notifications as read: {str(e)}"
        )
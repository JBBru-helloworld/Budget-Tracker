# backend/app/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from firebase_admin import auth as firebase_auth
from firebase_admin.exceptions import FirebaseError
from ..models.models import UserProfile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..services.firebase_service import verify_firebase_token
from datetime import datetime

router = APIRouter()
security = HTTPBearer()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(request: Request, user_data: dict = Body(...)):
    """
    Register a new user with Firebase Auth and create a profile in MongoDB
    """
    try:
        # Check if user already exists in MongoDB
        existing_user = await request.app.mongodb["user_profiles"].find_one({"email": user_data["email"]})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # User will be registered via Firebase Auth in the frontend
        # Here we just create a MongoDB profile
        user_profile = UserProfile(
            user_id=user_data["user_id"],
            email=user_data["email"],
            display_name=user_data.get("display_name")
        )
        
        # Insert user profile in MongoDB
        await request.app.mongodb["user_profiles"].insert_one(user_profile.dict(by_alias=True))
        
        return {"message": "User registered successfully"}
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering user: {str(e)}"
        )

@router.get("/me")
async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Retrieve currently authenticated user profile
    """
    try:
        # Verify Firebase token
        token = credentials.credentials
        user_data = await verify_firebase_token(token)
        user_id = user_data["uid"]
        
        # Get user profile from MongoDB
        user_profile = await request.app.mongodb["user_profiles"].find_one({"user_id": user_id})
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        # Convert ObjectId to string
        user_profile["_id"] = str(user_profile["_id"])
        
        return user_profile
    
    except FirebaseError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Firebase authentication failed: {str(e)}"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user profile: {str(e)}"
        )

@router.put("/profile")
async def update_user_profile(
    request: Request,
    user_data: dict = Body(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Update user profile
    """
    try:
        # Verify Firebase token
        token = credentials.credentials
        user_data_token = await verify_firebase_token(token)
        user_id = user_data_token["uid"]
        
        # Update user profile in MongoDB
        result = await request.app.mongodb["user_profiles"].update_one(
            {"user_id": user_id},
            {"$set": {
                "display_name": user_data.get("display_name"),
                "budget_targets": user_data.get("budget_targets", {}),
                "updated_at": datetime.utcnow()
            }}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return {"message": "User profile updated successfully"}
    
    except FirebaseError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Firebase authentication failed: {str(e)}"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user profile: {str(e)}"
        )
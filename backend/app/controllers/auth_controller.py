# app/controllers/auth_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
import firebase_admin
from firebase_admin import auth, credentials
from app.models.user_model import UserCreate, UserResponse
from app.services.user_service import create_user_profile

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """
    Register a new user with Firebase Auth and create a profile in MongoDB
    """
    try:
        # Create user in Firebase
        firebase_user = auth.create_user(
            email=user_data.email,
            password=user_data.password,
            display_name=user_data.display_name
        )
        
        # Create user profile in MongoDB
        user_profile = await create_user_profile({
            "firebase_uid": firebase_user.uid,
            "email": user_data.email,
            "display_name": user_data.display_name
        })
        
        return {
            "uid": firebase_user.uid,
            "email": firebase_user.email,
            "display_name": firebase_user.display_name,
            "message": "User registered successfully"
        }
    except firebase_admin.exceptions.FirebaseError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create Firebase user: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering user: {str(e)}"
        )

@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(email: str, password: str):
    """
    Verify user credentials with Firebase Authentication
    Note: This is a backend validation endpoint. Actual token creation
    should happen in the frontend using Firebase SDK.
    """
    # This route can be used for additional validation if needed
    # Actual Firebase authentication happens in the frontend
    return {"message": "Authentication handled by Firebase client SDK"}

@router.get("/verify-token", response_model=UserResponse)
async def verify_token(token: str = Depends(oauth2_scheme)):
    """
    Verify Firebase ID token and return user information
    """
    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        user = auth.get_user(uid)
        
        return {
            "uid": user.uid,
            "email": user.email,
            "display_name": user.display_name,
            "message": "Token verified"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    
@router.post("/register", response_model=UserCreate)
def register(user: UserCreate):
    print("Incoming register payload:", user)
    # …

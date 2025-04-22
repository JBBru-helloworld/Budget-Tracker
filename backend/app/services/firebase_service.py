# backend/app/services/firebase_service.py
import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin.exceptions import FirebaseError
from fastapi import HTTPException, status
from ..config import settings
import json

# Initialize Firebase Admin SDK
cred_dict = {
    "type": "service_account",
    "project_id": settings.FIREBASE_PROJECT_ID,
    "private_key": settings.FIREBASE_PRIVATE_KEY.replace('\\n', '\n'),
    "client_email": settings.FIREBASE_CLIENT_EMAIL,
    "token_uri": "https://oauth2.googleapis.com/token",
}

try:
    cred = credentials.Certificate(cred_dict)
    firebase_app = firebase_admin.initialize_app(cred)
except ValueError:
    # App already exists
    firebase_app = firebase_admin.get_app()

async def verify_firebase_token(token: str) -> str:
    """
    Verify Firebase ID token and return the user ID
    
    Args:
        token: Firebase ID token
        
    Returns:
        User ID from the token
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token["uid"]
    except FirebaseError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}"
        )
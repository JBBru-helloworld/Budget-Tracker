# backend/app/config/firebase.py
import firebase_admin
from firebase_admin import credentials
from ..config import settings
import os

def initialize_firebase():
    # Initialize Firebase Admin SDK as a singleton
    if not firebase_admin._apps:
        # Use service account file if available, otherwise use environment variables
        if os.path.exists(settings.FIREBASE_SERVICE_ACCOUNT_PATH):
            cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_PATH)
        else:
            # Use credential dictionary from environment variables
            cred_dict = {
                "type": "service_account",
                "project_id": settings.FIREBASE_PROJECT_ID,
                "private_key": settings.FIREBASE_PRIVATE_KEY.replace('\\n', '\n'),
                "client_email": settings.FIREBASE_CLIENT_EMAIL,
                "token_uri": "https://oauth2.googleapis.com/token",
            }
            cred = credentials.Certificate(cred_dict)
        
        # Initialize with storage bucket
        firebase_config = {
            'storageBucket': settings.FIREBASE_STORAGE_BUCKET
        }
        
        return firebase_admin.initialize_app(cred, firebase_config)
    else:
        return firebase_admin.get_app()

# Initialize Firebase on module import
firebase_app = initialize_firebase()
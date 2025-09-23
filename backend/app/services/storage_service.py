# backend/app/services/storage_service.py
import io
import os
from typing import Optional
from firebase_admin import storage
from fastapi import HTTPException, UploadFile
from ..config.firebase import firebase_app

class StorageService:
    def __init__(self):
        try:
            # Get bucket name from settings
            from ..config.settings import settings
            bucket_name = settings.FIREBASE_STORAGE_BUCKET
            
            if not bucket_name:
                print("WARNING: Firebase Storage bucket not configured. Avatar uploads will fail.")
                self.bucket = None
            else:
                self.bucket = storage.bucket(bucket_name, app=firebase_app)
                print(f"Firebase Storage initialized with bucket: {bucket_name}")
        except Exception as e:
            print(f"WARNING: Failed to initialize Firebase Storage: {str(e)}")
            self.bucket = None

    async def upload_avatar(self, file: UploadFile, user_id: str) -> str:
        """
        Upload avatar image to Firebase Storage and return the public URL
        
        Args:
            file: The uploaded image file
            user_id: The user's unique ID
            
        Returns:
            str: Public URL of the uploaded image
            
        Raises:
            HTTPException: If upload fails
        """
        if not self.bucket:
            raise HTTPException(
                status_code=500, 
                detail="Firebase Storage not configured"
            )
            
        try:
            # Validate file type
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
            if not file.filename:
                raise HTTPException(status_code=400, detail="No filename provided")
            
            file_ext = file.filename.split('.')[-1].lower()
            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Avatar must be one of {', '.join(allowed_extensions)}"
                )

            # Validate file size (5MB limit)
            file_content = await file.read()
            if len(file_content) > 5 * 1024 * 1024:  # 5MB
                raise HTTPException(
                    status_code=400, 
                    detail="Avatar file size must be less than 5MB"
                )

            # Create blob path
            blob_name = f"avatars/{user_id}.{file_ext}"
            blob = self.bucket.blob(blob_name)

            # Set content type
            content_type = f"image/{file_ext}" if file_ext != 'jpg' else "image/jpeg"
            
            # Upload file
            blob.upload_from_file(
                io.BytesIO(file_content), 
                content_type=content_type
            )

            # Make the blob public
            blob.make_public()

            # Return public URL
            public_url = blob.public_url
            return public_url

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error uploading avatar: {str(e)}"
            )

    async def delete_avatar(self, user_id: str) -> bool:
        """
        Delete user's avatar from Firebase Storage
        
        Args:
            user_id: The user's unique ID
            
        Returns:
            bool: True if deleted successfully, False if not found
        """
        if not self.bucket:
            print("Firebase Storage not configured - cannot delete avatar")
            return False
            
        try:
            # Try to delete common image formats
            extensions = ['png', 'jpg', 'jpeg', 'gif', 'webp']
            deleted = False
            
            for ext in extensions:
                blob_name = f"avatars/{user_id}.{ext}"
                blob = self.bucket.blob(blob_name)
                
                if blob.exists():
                    blob.delete()
                    deleted = True
                    
            return deleted
            
        except Exception as e:
            print(f"Error deleting avatar: {str(e)}")
            return False

    def get_avatar_url(self, user_id: str, file_extension: str = "png") -> Optional[str]:
        """
        Get the public URL for a user's avatar
        
        Args:
            user_id: The user's unique ID
            file_extension: The file extension (default: png)
            
        Returns:
            Optional[str]: Public URL if avatar exists, None otherwise
        """
        if not self.bucket:
            return None
            
        try:
            blob_name = f"avatars/{user_id}.{file_extension}"
            blob = self.bucket.blob(blob_name)
            
            if blob.exists():
                return blob.public_url
            return None
            
        except Exception as e:
            print(f"Error getting avatar URL: {str(e)}")
            return None

# Create a singleton instance
storage_service = StorageService()

# Legacy function for backwards compatibility (for receipts)
async def upload_image(file: UploadFile, filename: str) -> str:
    """
    Legacy upload function for receipts - still uses local storage
    TODO: Migrate receipts to Firebase Storage as well
    """
    from pathlib import Path
    import aiofiles
    
    UPLOAD_DIR = Path("uploads")
    
    try:
        # Ensure upload directory exists
        full_path = UPLOAD_DIR / filename
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Save the file
        async with aiofiles.open(full_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)
            
        # Reset file position for future reads
        await file.seek(0)
        
        # Return the local path
        return f"/uploads/{filename}"
        
    except Exception as e:
        raise Exception(f"Error uploading file: {str(e)}")
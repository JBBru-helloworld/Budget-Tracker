# backend/app/services/storage_service.py
from fastapi import UploadFile
import os
import aiofiles
from pathlib import Path
import uuid

# Directory to store uploaded files
UPLOAD_DIR = Path("uploads")

async def upload_image(file: UploadFile, filename: str) -> str:
    """
    Upload an image file to local storage (in a production environment, 
    this would be replaced with cloud storage like S3, GCS, etc.)
    
    Args:
        file: The uploaded file
        filename: Desired filename including path
        
    Returns:
        str: URL to access the uploaded file
    """
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
        
        # In production, return a proper URL to the file
        # For now, return the local path
        return f"/uploads/{filename}"
        
    except Exception as e:
        raise Exception(f"Error uploading file: {str(e)}")
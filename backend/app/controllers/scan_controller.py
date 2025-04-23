# app/controllers/scan_controller.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from typing import List
import os
from app.models.receipt_model import ReceiptItem
from app.services.ai_service import extract_text_from_image, categorize_items
from app.controllers.auth_controller import verify_token

router = APIRouter()

@router.post("/scan", response_model=List[ReceiptItem])
async def scan_receipt(
    file: UploadFile = File(...),
    user_id: str = Depends(verify_token)
):
    """
    Scan a receipt image and extract items using AI without saving to database
    """
    # Validate image format
    allowed_extensions = ["jpg", "jpeg", "png"]
    file_ext = file.filename.split(".")[-1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File must be one of {', '.join(allowed_extensions)}"
        )
    
    try:
        # Save image temporarily
        file_path = f"temp/{file.filename}"
        os.makedirs("temp", exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # Extract text from image using AI
        items_text = await extract_text_from_image(file_path)
        
        # Process and categorize items
        receipt_items = await categorize_items(items_text)
        
        return receipt_items
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scanning receipt: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if os.path.exists(file_path):
            os.remove(file_path)
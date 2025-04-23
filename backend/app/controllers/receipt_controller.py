# app/controllers/receipt_controller.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from typing import List, Optional
import os
from datetime import datetime
from bson import ObjectId
from app.models.receipt_model import ReceiptCreate, ReceiptResponse, ReceiptItem
from app.services.receipt_service import save_receipt, get_receipt, get_user_receipts, delete_receipt, update_receipt
from app.services.ai_service import extract_text_from_image, categorize_items
from app.controllers.auth_controller import verify_token

router = APIRouter()

@router.post("/upload", response_model=ReceiptResponse)
async def upload_receipt(
    file: UploadFile = File(...),
    store_name: str = Form(...),
    date: str = Form(...),
    user_id: str = Depends(verify_token)
):
    """
    Upload a receipt image, extract items using AI, and save to database
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
        
        # Create receipt object
        receipt_data = {
            "user_id": user_id["uid"],
            "store_name": store_name,
            "date": datetime.strptime(date, "%Y-%m-%d"),
            "items": receipt_items,
            "total_amount": sum(item.price for item in receipt_items),
            "image_path": file_path,
            "shared_with": []
        }
        
        # Save receipt to database
        receipt_id = await save_receipt(receipt_data)
        
        return {
            "id": str(receipt_id),
            "message": "Receipt uploaded and processed successfully",
            "items": receipt_items,
            "total_amount": receipt_data["total_amount"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing receipt: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

@router.get("/{receipt_id}", response_model=ReceiptResponse)
async def get_receipt_detail(receipt_id: str, user_id: str = Depends(verify_token)):
    """
    Get detailed information about a specific receipt
    """
    try:
        receipt = await get_receipt(ObjectId(receipt_id), user_id["uid"])
        if not receipt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receipt not found"
            )
        
        return receipt
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching receipt: {str(e)}"
        )

@router.get("/", response_model=List[ReceiptResponse])
async def list_receipts(
    user_id: str = Depends(verify_token),
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Get all receipts for the authenticated user with optional filtering
    """
    date_filters = {}
    
    if start_date:
        date_filters["start"] = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        date_filters["end"] = datetime.strptime(end_date, "%Y-%m-%d")
    
    try:
        receipts = await get_user_receipts(
            user_id["uid"],
            skip=skip,
            limit=limit,
            category=category,
            date_filters=date_filters
        )
        return receipts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching receipts: {str(e)}"
        )

@router.put("/{receipt_id}", response_model=ReceiptResponse)
async def update_receipt_items(
    receipt_id: str,
    updates: dict,
    user_id: str = Depends(verify_token)
):
    """
    Update receipt details or shared status
    """
    try:
        updated_receipt = await update_receipt(ObjectId(receipt_id), user_id["uid"], updates)
        if not updated_receipt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receipt not found or you don't have permission to update it"
            )
        
        return updated_receipt
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating receipt: {str(e)}"
        )

@router.delete("/{receipt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_receipt(receipt_id: str, user_id: str = Depends(verify_token)):
    """
    Delete a receipt
    """
    try:
        result = await delete_receipt(ObjectId(receipt_id), user_id["uid"])
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receipt not found or you don't have permission to delete it"
            )
        
        return {"message": "Receipt deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting receipt: {str(e)}"
        )
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from ..models.receipt_model import Receipt, ReceiptCreate, ReceiptResponse, ReceiptItem
from ..services.ocr_service import process_receipt_image
from ..services.firebase_service import get_user_id_from_token
from ..services.receipt_service import get_user_receipts, save_receipt
from ..config.mongodb import get_database
from bson import ObjectId
from datetime import datetime

router = APIRouter(
    prefix="/receipts",
    tags=["receipts"]
)

@router.get("/")
async def get_receipts(
    firebase_uid: str = Depends(get_user_id_from_token),
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Get all receipts for the authenticated user
    """
    try:
        # Build date filters
        date_filters = {}
        if start_date:
            date_filters["start"] = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            date_filters["end"] = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Get receipts from service
        receipts = await get_user_receipts(
            firebase_uid,
            skip=skip,
            limit=limit,
            category=category,
            date_filters=date_filters
        )
        
        return receipts
        
    except Exception as e:
        print(f"Error fetching receipts for user {firebase_uid}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch receipts: {str(e)}"
        )

@router.post("/scan")
async def scan_receipt(
    image_data: str = Body(..., embed=True),
    firebase_uid: str = Depends(get_user_id_from_token)
):
    # Process a receipt image using OCR
    try:
        # Process the image with Gemini OCR
        receipt_data = await process_receipt_image(image_data)
        
        if "error" in receipt_data:
            return JSONResponse(
                status_code=400,
                content={"message": f"Failed to process receipt: {receipt_data['error']}"}
            )
            
        # Return the extracted data
        return receipt_data
        
    except Exception as e:
        print(f"Receipt scanning error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"message": f"Error processing receipt: {str(e)}"}
        )

@router.post("/")
async def create_receipt(
    receipt: ReceiptCreate,
    firebase_uid: str = Depends(get_user_id_from_token)
):
    # Create a new receipt in the database
    try:
        # Prepare receipt data for database
        receipt_dict = receipt.dict()
        receipt_dict["user_id"] = firebase_uid
        
        # Save the receipt using the service
        saved_receipt = await save_receipt(receipt_dict)
        
        return saved_receipt
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create receipt: {str(e)}"
        )
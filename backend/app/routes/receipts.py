from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from ..models.receipt_model import Receipt, ReceiptCreate, ReceiptResponse, ReceiptItem
from ..services.ocr_service import process_receipt_image
from ..services.firebase_service import verify_firebase_token
from ..config.mongodb import get_database
from bson import ObjectId
from datetime import datetime

router = APIRouter(
    prefix="/receipts",
    tags=["receipts"]
)

@router.post("/scan")
async def scan_receipt(
    image_data: str = Body(..., embed=True),
    firebase_uid: str = Depends(verify_firebase_token)
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
    firebase_uid: str = Depends(verify_firebase_token)
):
    # Create a new receipt in the database
    try:
        db = get_database()
        
        # Prepare receipt data for database
        receipt_dict = receipt.dict()
        receipt_dict["user_id"] = firebase_uid
        receipt_dict["created_at"] = datetime.now()
        receipt_dict["updated_at"] = datetime.now()
        
        # Insert the receipt into MongoDB
        result = db.receipts.insert_one(receipt_dict)
        receipt_id = str(result.inserted_id)
        
        # Return the created receipt with ID
        response_data = receipt_dict.copy()
        response_data["id"] = receipt_id
        if "_id" in response_data:
            del response_data["_id"]
        
        return response_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create receipt: {str(e)}"
        )
# backend/app/routes/receipts.py
from fastapi import APIRouter, Body, Depends, HTTPException, Request, status, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..models.models import Receipt, ReceiptItem, Category
from ..services.ai_service import process_receipt_image
from ..services.storage_service import upload_image
from datetime import datetime
import uuid
from typing import List, Optional
from bson import ObjectId

router = APIRouter()
security = HTTPBearer()

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_receipt(
    request: Request,
    receipt_image: UploadFile = File(...),
    store_name: str = Form(...),
    date: str = Form(...),  # Format: YYYY-MM-DD
    notes: Optional[str] = Form(None),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Upload a receipt image and process it with AI
    """
    try:
        user_id = request.state.user_id
        
        # Validate image format
        allowed_formats = ["image/jpeg", "image/jpg", "image/png"]
        if receipt_image.content_type not in allowed_formats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image must be in JPG, JPEG, or PNG format"
            )
        
        # Generate unique filename
        file_extension = receipt_image.filename.split(".")[-1]
        filename = f"receipts/{user_id}/{uuid.uuid4()}.{file_extension}"
        
        # Upload image to storage service
        image_url = await upload_image(receipt_image, filename)
        
        # Process receipt with AI
        receipt_date = datetime.fromisoformat(date)
        receipt_data = await process_receipt_image(receipt_image, store_name, receipt_date)
        
        # Create receipt object
        receipt = Receipt(
            user_id=user_id,
            date=receipt_date,
            store_name=store_name,
            total_amount=receipt_data["total_amount"],
            items=receipt_data["items"],
            image_url=image_url,
            raw_text=receipt_data["raw_text"],
            notes=notes
        )
        
        # Save to database
        result = await request.app.mongodb["receipts"].insert_one(receipt.dict(by_alias=True))
        
        # Get created receipt with ID
        created_receipt = await request.app.mongodb["receipts"].find_one({"_id": result.inserted_id})
        created_receipt["_id"] = str(created_receipt["_id"])
        
        return created_receipt
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing receipt: {str(e)}"
        )

@router.get("/", response_model=List[dict])
async def get_receipts(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    skip: int = 0,
    limit: int = 10
):
    """
    Get list of receipts for the authenticated user
    """
    try:
        user_id = request.state.user_id
        
        # Query database
        cursor = request.app.mongodb["receipts"].find({"user_id": user_id})
        cursor.sort("date", -1).skip(skip).limit(limit)
        
        # Convert to list and format IDs
        receipts = []
        async for receipt in cursor:
            receipt["_id"] = str(receipt["_id"])
            receipts.append(receipt)
        
        return receipts
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving receipts: {str(e)}"
        )

@router.get("/{receipt_id}")
async def get_receipt(
    receipt_id: str,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get a specific receipt by ID
    """
    try:
        user_id = request.state.user_id
        
        # Validate ObjectId
        if not ObjectId.is_valid(receipt_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid receipt ID"
            )
        
        # Query database
        receipt = await request.app.mongodb["receipts"].find_one({
            "_id": ObjectId(receipt_id),
            "user_id": user_id
        })
        
        if not receipt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receipt not found"
            )
        
        # Format ID
        receipt["_id"] = str(receipt["_id"])
        
        return receipt
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving receipt: {str(e)}"
        )

@router.put("/{receipt_id}/items")
async def update_receipt_items(
    receipt_id: str,
    items: List[dict] = Body(...),
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Update receipt items (assign to people, categorize, etc.)
    """
    try:
        user_id = request.state.user_id
        
        # Validate ObjectId
        if not ObjectId.is_valid(receipt_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid receipt ID"
            )
        
        # Update items in database
        result = await request.app.mongodb["receipts"].update_one(
            {"_id": ObjectId(receipt_id), "user_id": user_id},
            {"$set": {"items": items, "updated_at": datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receipt not found"
            )
            
        # Calculate and update total amount
        total_amount = sum(item["price"] * item.get("quantity", 1) for item in items)
        await request.app.mongodb["receipts"].update_one(
            {"_id": ObjectId(receipt_id)},
            {"$set": {"total_amount": total_amount}}
        )
        
        return {"message": "Receipt items updated successfully"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating receipt items: {str(e)}"
        )

@router.delete("/{receipt_id}")
async def delete_receipt(
    receipt_id: str,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Delete a receipt
    """
    try:
        user_id = request.state.user_id
        
        # Validate ObjectId
        if not ObjectId.is_valid(receipt_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid receipt ID"
            )
        
        # Delete receipt
        result = await request.app.mongodb["receipts"].delete_one({
            "_id": ObjectId(receipt_id),
            "user_id": user_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receipt not found"
            )
        
        return {"message": "Receipt deleted successfully"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting receipt: {str(e)}"
        )
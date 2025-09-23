# app/controllers/scan_controller.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from typing import List
import os
import shutil
from app.services.firebase_service import get_user_id_from_token
from app.services.ocr_service import process_receipt_image
from app.models.receipt_model import ProcessedReceiptResponse
import uuid

router = APIRouter()

@router.post("/receipt", response_model=ProcessedReceiptResponse)
async def scan_receipt(
    file: UploadFile = File(...),
    user_id: str = Depends(get_user_id_from_token)
):
    """
    Scan and process a receipt image
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{file_extension}"
        file_path = f"uploads/{filename}"
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        try:
            # Process receipt image using OCR and AI
            receipt_data = await process_receipt_image(file_path, is_base64=False)
            
            if "error" in receipt_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Could not process receipt: {receipt_data['error']}"
                )
            
            # Return the processed receipt data
            return ProcessedReceiptResponse(
                extracted_text=str(receipt_data),
                processed_data=receipt_data,
                image_path=file_path
            )
            
        finally:
            # Clean up uploaded file
            if os.path.exists(file_path):
                os.remove(file_path)
                
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing receipt: {str(e)}"
        )

@router.post("/text")
async def process_receipt_text_endpoint(
    text: str,
    user_id: str = Depends(get_user_id_from_token)
):
    """
    Process receipt text directly without image upload
    """
    try:
        if not text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text cannot be empty"
            )
        
        # Process the text with AI using Gemini text model
        import google.generativeai as genai
        text_model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        Analyze this receipt text and extract the following information:
        1. Store name
        2. Date (in ISO format)
        3. Total amount
        4. Individual items with names and prices
        5. Categories for each item (food, clothing, recreation, transport, household, healthcare, education, other)
        
        Receipt text: {text}
        
        Return as JSON with this structure:
        {{
          "store_name": "Store Name",
          "date": "2023-01-01",
          "total_amount": 0.00,
          "items": [
            {{"name": "Item", "price": 0.00, "category": "food"}}
          ]
        }}
        """
        
        response = text_model.generate_content(prompt)
        import json
        result_text = response.text
        if '```json' in result_text:
            result_text = result_text.split('```json')[1].split('```')[0].strip()
        elif '```' in result_text:
            result_text = result_text.split('```')[1].split('```')[0].strip()
        
        processed_receipt = json.loads(result_text)
        
        return {
            "processed_data": processed_receipt
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing text: {str(e)}"
        )

@router.post("/receipt-base64", response_model=ProcessedReceiptResponse)
async def scan_receipt_base64(
    image_data: dict,
    user_id: str = Depends(get_user_id_from_token)
):
    """
    Scan and process a receipt from base64 image data
    """
    try:
        base64_image = image_data.get("image_data")
        if not base64_image:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="image_data is required"
            )
        
        # Process the base64 image data
        receipt_data = await process_receipt_image(base64_image, is_base64=True)
        
        # Check if there's an error but still return partial data
        if "error" in receipt_data:
            print(f"Warning: Receipt processing had issues: {receipt_data['error']}")
            # Don't raise an error if we got some data back
            if receipt_data.get("store_name") or receipt_data.get("items"):
                # Return partial data with warning
                return ProcessedReceiptResponse(
                    extracted_text=f"Warning: {receipt_data['error']}\n\nPartial data extracted",
                    processed_data=receipt_data,
                    image_path=""
                )
            else:
                # Only raise error if we got no useful data
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"AI service temporarily unavailable: {receipt_data['error']}. Please try again in a few moments."
                )
        
        # Return the processed receipt data
        return ProcessedReceiptResponse(
            extracted_text=str(receipt_data),
            processed_data=receipt_data,
            image_path=""  # No file path for base64 data
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"Unexpected error in scan_receipt_base64: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the receipt. Please try again."
        )
